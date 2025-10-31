"""
Matching Engine
Implements REG NMS-inspired price-time priority matching
Prevents trade-throughs and ensures best execution
"""
from decimal import Decimal
from typing import List, Optional, Dict, Callable
from datetime import datetime
import logging
from threading import Lock

from .order import Order, OrderType, OrderSide, OrderStatus
from .trade import Trade
from .order_book import OrderBook

logger = logging.getLogger(__name__)

class MatchingEngine:
    """
    High-performance matching engine with REG NMS principles:
    - Price-time priority
    - Internal order protection
    - No trade-throughs
    """
    def __init__(self):
        self.books: Dict[str, OrderBook] = {}
        self.trades: List[Trade] = []
        self.lock = Lock()  # Thread safety
        
        # Callbacks for real-time updates
        self.on_trade_callbacks: List[Callable] = []
        self.on_book_update_callbacks: List[Callable] = []
        
        logger.info("Matching engine initialized")
    
    def register_trade_callback(self, callback: Callable):
        """Register callback for trade executions"""
        self.on_trade_callbacks.append(callback)
    
    def register_book_update_callback(self, callback: Callable):
        """Register callback for order book updates"""
        self.on_book_update_callbacks.append(callback)
    
    def _get_or_create_book(self, symbol: str) -> OrderBook:
        """Get or create order book for symbol"""
        if symbol not in self.books:
            self.books[symbol] = OrderBook(symbol)
            logger.info(f"Created order book for {symbol}")
        return self.books[symbol]
    
    def submit_order(self, order: Order) -> dict:
        """
        Submit order to matching engine
        Returns execution report
        """
        with self.lock:
            try:
                logger.info(f"Processing order: {order.order_id} - {order.order_type.value} "
                           f"{order.side.value} {order.quantity} {order.symbol} @ {order.price}")
                
                book = self._get_or_create_book(order.symbol)
                
                # Handle different order types
                if order.order_type == OrderType.MARKET:
                    return self._process_market_order(order, book)
                elif order.order_type == OrderType.LIMIT:
                    return self._process_limit_order(order, book)
                elif order.order_type == OrderType.IOC:
                    return self._process_ioc_order(order, book)
                elif order.order_type == OrderType.FOK:
                    return self._process_fok_order(order, book)
                
            except Exception as e:
                logger.error(f"Error processing order {order.order_id}: {e}", exc_info=True)
                order.status = OrderStatus.REJECTED
                return {
                    'success': False,
                    'order': order.to_dict(),
                    'message': str(e),
                    'trades': []
                }
    
    def _process_market_order(self, order: Order, book: OrderBook) -> dict:
        """Process market order - execute immediately at best available prices"""
        trades = self._match_order(order, book)
        
        if order.remaining_quantity > 0:
            # Market order with remaining quantity is cancelled
            order.status = OrderStatus.CANCELLED
            logger.warning(f"Market order {order.order_id} partially filled and cancelled. "
                         f"Filled: {order.filled_quantity}, Remaining: {order.remaining_quantity}")
        else:
            order.status = OrderStatus.FILLED
        
        self._notify_book_update(book)
        
        return {
            'success': True,
            'order': order.to_dict(),
            'message': f'Market order {"filled" if order.status == OrderStatus.FILLED else "partially filled"}',
            'trades': [t.to_dict() for t in trades]
        }
    
    def _process_limit_order(self, order: Order, book: OrderBook) -> dict:
        """Process limit order - match if possible, otherwise rest on book"""
        trades = self._match_order(order, book)
        
        if order.remaining_quantity > 0:
            # Add remaining quantity to book
            book.add_order(order)
            order.status = OrderStatus.PARTIAL if order.filled_quantity > 0 else OrderStatus.PENDING
            logger.info(f"Limit order {order.order_id} resting on book with "
                       f"{order.remaining_quantity} remaining")
        else:
            order.status = OrderStatus.FILLED
        
        self._notify_book_update(book)
        
        return {
            'success': True,
            'order': order.to_dict(),
            'message': 'Limit order processed',
            'trades': [t.to_dict() for t in trades]
        }
    
    def _process_ioc_order(self, order: Order, book: OrderBook) -> dict:
        """Process IOC order - execute immediately, cancel unfilled portion"""
        trades = self._match_order(order, book)
        
        if order.remaining_quantity > 0:
            order.status = OrderStatus.CANCELLED
            logger.info(f"IOC order {order.order_id} cancelled with "
                       f"{order.remaining_quantity} unfilled")
        else:
            order.status = OrderStatus.FILLED
        
        self._notify_book_update(book)
        
        return {
            'success': True,
            'order': order.to_dict(),
            'message': 'IOC order processed',
            'trades': [t.to_dict() for t in trades]
        }
    
    def _process_fok_order(self, order: Order, book: OrderBook) -> dict:
        """Process FOK order - fill completely or cancel"""
        # Check if order can be fully filled
        if not self._can_fill_quantity(order, book):
            order.status = OrderStatus.CANCELLED
            logger.info(f"FOK order {order.order_id} cancelled - cannot be fully filled")
            return {
                'success': False,
                'order': order.to_dict(),
                'message': 'FOK order cancelled - insufficient liquidity',
                'trades': []
            }
        
        # Order can be filled - execute
        trades = self._match_order(order, book)
        order.status = OrderStatus.FILLED
        
        self._notify_book_update(book)
        
        return {
            'success': True,
            'order': order.to_dict(),
            'message': 'FOK order filled',
            'trades': [t.to_dict() for t in trades]
        }
    
    def _can_fill_quantity(self, order: Order, book: OrderBook) -> bool:
        """Check if order can be completely filled at acceptable prices"""
        available_quantity = Decimal('0')
        
        if order.side == OrderSide.BUY:
            # Check asks
            for key, price_level in book.asks.items():
                if order.price and price_level.price > order.price:
                    break
                available_quantity += price_level.total_quantity
                if available_quantity >= order.quantity:
                    return True
        else:
            # Check bids
            for key, price_level in book.bids.items():
                if order.price and price_level.price < order.price:
                    break
                available_quantity += price_level.total_quantity
                if available_quantity >= order.quantity:
                    return True
        
        return False
    
    def _match_order(self, order: Order, book: OrderBook) -> List[Trade]:
        """
        Match order against order book using price-time priority
        Prevents trade-throughs by ensuring best price execution
        """
        trades = []
        
        if order.side == OrderSide.BUY:
            trades = self._match_against_asks(order, book)
        else:
            trades = self._match_against_bids(order, book)
        
        return trades
    
    def _match_against_asks(self, buy_order: Order, book: OrderBook) -> List[Trade]:
        """Match buy order against asks"""
        trades = []
        
        while buy_order.remaining_quantity > 0 and book.asks:
            best_ask_price = book.get_best_ask()
            
            # Check if order is marketable at this price
            if buy_order.price and buy_order.price < best_ask_price:
                break
            
            # Get orders at best ask price
            ask_key = best_ask_price
            if ask_key not in book.asks:
                break
            
            price_level = book.asks[ask_key]
            
            # Match against orders at this price level (FIFO)
            while buy_order.remaining_quantity > 0 and not price_level.is_empty():
                sell_order = price_level.get_first_order()
                if not sell_order:
                    break
                
                # Execute trade
                trade = self._execute_trade(buy_order, sell_order, sell_order.price)
                trades.append(trade)
                
                # Update orders
                if sell_order.remaining_quantity == 0:
                    price_level.orders.popleft()
                    sell_order.status = OrderStatus.FILLED
                    del book.order_map[sell_order.order_id]
            
            # Remove empty price level
            if price_level.is_empty():
                del book.asks[ask_key]
        
        return trades
    
    def _match_against_bids(self, sell_order: Order, book: OrderBook) -> List[Trade]:
        """Match sell order against bids"""
        trades = []
        
        while sell_order.remaining_quantity > 0 and book.bids:
            best_bid_price = book.get_best_bid()
            
            # Check if order is marketable at this price
            if sell_order.price and sell_order.price > best_bid_price:
                break
            
            # Get orders at best bid price
            bid_key = -best_bid_price
            if bid_key not in book.bids:
                break
            
            price_level = book.bids[bid_key]
            
            # Match against orders at this price level (FIFO)
            while sell_order.remaining_quantity > 0 and not price_level.is_empty():
                buy_order = price_level.get_first_order()
                if not buy_order:
                    break
                
                # Execute trade
                trade = self._execute_trade(sell_order, buy_order, buy_order.price)
                trades.append(trade)
                
                # Update orders
                if buy_order.remaining_quantity == 0:
                    price_level.orders.popleft()
                    buy_order.status = OrderStatus.FILLED
                    del book.order_map[buy_order.order_id]
            
            # Remove empty price level
            if price_level.is_empty():
                del book.bids[bid_key]
        
        return trades
    
    def _execute_trade(self, taker_order: Order, maker_order: Order, 
                      price: Decimal) -> Trade:
        """Execute a trade between two orders"""
        quantity = min(taker_order.remaining_quantity, maker_order.remaining_quantity)
        
        # Update orders
        taker_order.remaining_quantity -= quantity
        taker_order.filled_quantity += quantity
        maker_order.remaining_quantity -= quantity
        maker_order.filled_quantity += quantity
        
        # Create trade
        trade = Trade.create_trade(
            symbol=taker_order.symbol,
            price=price,
            quantity=quantity,
            aggressor_side=taker_order.side.value,
            maker_order_id=maker_order.order_id,
            taker_order_id=taker_order.order_id
        )
        
        self.trades.append(trade)
        
        logger.info(f"Trade executed: {trade.trade_id} - {quantity} @ {price}")
        
        # Notify callbacks
        self._notify_trade(trade)
        
        return trade
    
    def _notify_trade(self, trade: Trade):
        """Notify all trade callbacks"""
        for callback in self.on_trade_callbacks:
            try:
                callback(trade)
            except Exception as e:
                logger.error(f"Error in trade callback: {e}")
    
    def _notify_book_update(self, book: OrderBook):
        """Notify all book update callbacks"""
        for callback in self.on_book_update_callbacks:
            try:
                callback(book)
            except Exception as e:
                logger.error(f"Error in book update callback: {e}")
    
    def cancel_order(self, symbol: str, order_id: str) -> dict:
        """Cancel an order"""
        with self.lock:
            book = self.books.get(symbol)
            if not book:
                return {
                    'success': False,
                    'message': f'No order book found for {symbol}'
                }
            
            order = book.remove_order(order_id)
            if not order:
                return {
                    'success': False,
                    'message': f'Order {order_id} not found'
                }
            
            order.status = OrderStatus.CANCELLED
            self._notify_book_update(book)
            
            logger.info(f"Order cancelled: {order_id}")
            
            return {
                'success': True,
                'message': 'Order cancelled',
                'order': order.to_dict()
            }
    
    def get_order_book(self, symbol: str, depth: int = 10) -> dict:
        """Get current order book state"""
        book = self.books.get(symbol)
        if not book:
            return {
                'timestamp': datetime.utcnow().isoformat() + 'Z',
                'symbol': symbol,
                'bids': [],
                'asks': []
            }
        return book.get_depth(depth)
    
    def get_bbo(self, symbol: str) -> dict:
        """Get Best Bid and Offer"""
        book = self.books.get(symbol)
        if not book:
            return {
                'symbol': symbol,
                'bid': None,
                'ask': None,
                'spread': None
            }
        
        bid, ask = book.get_bbo()
        spread = book.get_spread()
        
        return {
            'symbol': symbol,
            'bid': str(bid) if bid else None,
            'ask': str(ask) if ask else None,
            'spread': str(spread) if spread else None
        }