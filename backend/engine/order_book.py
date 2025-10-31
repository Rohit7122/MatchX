"""
Order Book Implementation
Maintains bids and asks with price-time priority
Uses SortedDict for O(log n) operations and fast BBO calculation
"""
from sortedcontainers import SortedDict
from collections import deque
from decimal import Decimal
from typing import Optional, List, Tuple, Dict
from datetime import datetime
import logging

from .order import Order, OrderSide

logger = logging.getLogger(__name__)

class PriceLevel:
    """Represents all orders at a specific price level"""
    def __init__(self, price: Decimal):
        self.price = price
        self.orders = deque()  # FIFO queue for time priority
        self.total_quantity = Decimal('0')
    
    def add_order(self, order: Order):
        """Add order to this price level"""
        self.orders.append(order)
        self.total_quantity += order.remaining_quantity
    
    def remove_order(self, order: Order) -> bool:
        """Remove order from this price level"""
        try:
            self.orders.remove(order)
            self.total_quantity -= order.remaining_quantity
            return True
        except ValueError:
            return False
    
    def is_empty(self) -> bool:
        """Check if price level has any orders"""
        return len(self.orders) == 0
    
    def get_first_order(self) -> Optional[Order]:
        """Get the oldest order at this price level"""
        return self.orders[0] if self.orders else None

class OrderBook:
    """
    Order book maintaining bids and asks with price-time priority
    Bids: sorted descending (highest price first)
    Asks: sorted ascending (lowest price first)
    """
    def __init__(self, symbol: str):
        self.symbol = symbol
        # Bids: negative keys for descending sort
        self.bids = SortedDict()
        # Asks: positive keys for ascending sort
        self.asks = SortedDict()
        # Order ID to Order mapping for quick lookup
        self.order_map: Dict[str, Order] = {}
        self.last_update = datetime.utcnow()
    
    def add_order(self, order: Order):
        """Add order to the appropriate side of the book"""
        if order.side == OrderSide.BUY:
            self._add_to_side(self.bids, order, is_bid=True)
        else:
            self._add_to_side(self.asks, order, is_bid=False)
        
        self.order_map[order.order_id] = order
        self.last_update = datetime.utcnow()
        logger.debug(f"Added order {order.order_id} to book: {order.side.value} "
                    f"{order.quantity} @ {order.price}")
    
    def _add_to_side(self, side: SortedDict, order: Order, is_bid: bool):
        """Add order to specific side of book"""
        # For bids, use negative price for descending sort
        key = -order.price if is_bid else order.price
        
        if key not in side:
            side[key] = PriceLevel(order.price)
        
        side[key].add_order(order)
    
    def remove_order(self, order_id: str) -> Optional[Order]:
        """Remove order from the book"""
        order = self.order_map.get(order_id)
        if not order:
            return None
        
        side = self.bids if order.side == OrderSide.BUY else self.asks
        key = -order.price if order.side == OrderSide.BUY else order.price
        
        if key in side:
            price_level = side[key]
            price_level.remove_order(order)
            
            # Remove empty price level
            if price_level.is_empty():
                del side[key]
        
        del self.order_map[order_id]
        self.last_update = datetime.utcnow()
        logger.debug(f"Removed order {order_id} from book")
        return order
    
    def get_best_bid(self) -> Optional[Decimal]:
        """Get best bid price (highest buy price)"""
        if not self.bids:
            return None
        # First key is most negative = highest price
        return -self.bids.keys()[0]
    
    def get_best_ask(self) -> Optional[Decimal]:
        """Get best ask price (lowest sell price)"""
        if not self.asks:
            return None
        return self.asks.keys()[0]
    
    def get_bbo(self) -> Tuple[Optional[Decimal], Optional[Decimal]]:
        """Get Best Bid and Offer"""
        return self.get_best_bid(), self.get_best_ask()
    
    def get_spread(self) -> Optional[Decimal]:
        """Calculate bid-ask spread"""
        bid, ask = self.get_bbo()
        if bid is None or ask is None:
            return None
        return ask - bid
    
    def get_depth(self, levels: int = 10) -> dict:
        """
        Get order book depth
        Returns top N levels of bids and asks
        """
        bids = []
        asks = []
        
        # Get bid levels (highest to lowest)
        for i, (key, price_level) in enumerate(self.bids.items()):
            if i >= levels:
                break
            bids.append([str(price_level.price), str(price_level.total_quantity)])
        
        # Get ask levels (lowest to highest)
        for i, (key, price_level) in enumerate(self.asks.items()):
            if i >= levels:
                break
            asks.append([str(price_level.price), str(price_level.total_quantity)])
        
        return {
            'timestamp': self.last_update.isoformat() + 'Z',
            'symbol': self.symbol,
            'bids': bids,
            'asks': asks
        }
    
    def get_orders_at_price(self, side: OrderSide, price: Decimal) -> List[Order]:
        """Get all orders at a specific price level"""
        book_side = self.bids if side == OrderSide.BUY else self.asks
        key = -price if side == OrderSide.BUY else price
        
        if key not in book_side:
            return []
        
        return list(book_side[key].orders)
    
    def clear(self):
        """Clear all orders from the book"""
        self.bids.clear()
        self.asks.clear()
        self.order_map.clear()
        self.last_update = datetime.utcnow()
        logger.info(f"Cleared order book for {self.symbol}")