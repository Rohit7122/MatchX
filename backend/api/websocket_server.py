"""
WebSocket Server
Real-time market data and trade feed distribution
"""
import asyncio
import json
import logging
from typing import Set
import websockets
from websockets.server import WebSocketServerProtocol

from engine.trade import Trade
from engine.order_book import OrderBook

logger = logging.getLogger(__name__)

class WebSocketServer:
    """WebSocket server for real-time market data"""
    
    def __init__(self, host: str = '0.0.0.0', port: int = 8765):
        self.host = host
        self.port = port
        self.trade_subscribers: Set[WebSocketServerProtocol] = set()
        self.book_subscribers: Set[WebSocketServerProtocol] = set()
        
    async def start(self):
        """Start WebSocket server"""
        async with websockets.serve(self.handler, self.host, self.port):
            logger.info(f"WebSocket server started on ws://{self.host}:{self.port}")
            await asyncio.Future()  # Run forever
    
    async def handler(self, websocket: WebSocketServerProtocol, path: str):
        """Handle WebSocket connections"""
        logger.info(f"New WebSocket connection from {websocket.remote_address}")
        
        try:
            # Send welcome message
            await websocket.send(json.dumps({
                'type': 'connected',
                'message': 'Connected to matching engine WebSocket',
                'available_channels': ['trades', 'orderbook']
            }))
            
            async for message in websocket:
                try:
                    data = json.loads(message)
                    await self.process_message(websocket, data)
                except json.JSONDecodeError:
                    await websocket.send(json.dumps({
                        'type': 'error',
                        'message': 'Invalid JSON'
                    }))
        except websockets.exceptions.ConnectionClosed:
            logger.info(f"WebSocket connection closed: {websocket.remote_address}")
        finally:
            # Clean up subscriptions
            self.trade_subscribers.discard(websocket)
            self.book_subscribers.discard(websocket)
    
    async def process_message(self, websocket: WebSocketServerProtocol, data: dict):
        """Process incoming WebSocket messages"""
        action = data.get('action')
        
        if action == 'subscribe':
            channel = data.get('channel')
            if channel == 'trades':
                self.trade_subscribers.add(websocket)
                await websocket.send(json.dumps({
                    'type': 'subscribed',
                    'channel': 'trades'
                }))
                logger.info(f"Client subscribed to trades")
            elif channel == 'orderbook':
                self.book_subscribers.add(websocket)
                await websocket.send(json.dumps({
                    'type': 'subscribed',
                    'channel': 'orderbook'
                }))
                logger.info(f"Client subscribed to orderbook")
        
        elif action == 'unsubscribe':
            channel = data.get('channel')
            if channel == 'trades':
                self.trade_subscribers.discard(websocket)
                await websocket.send(json.dumps({
                    'type': 'unsubscribed',
                    'channel': 'trades'
                }))
            elif channel == 'orderbook':
                self.book_subscribers.discard(websocket)
                await websocket.send(json.dumps({
                    'type': 'unsubscribed',
                    'channel': 'orderbook'
                }))
    
    async def broadcast_trade(self, trade: Trade):
        """Broadcast trade to all subscribers"""
        if not self.trade_subscribers:
            return
        
        message = json.dumps({
            'type': 'trade',
            'data': trade.to_dict()
        })
        
        # Send to all trade subscribers
        disconnected = set()
        for websocket in self.trade_subscribers:
            try:
                await websocket.send(message)
            except websockets.exceptions.ConnectionClosed:
                disconnected.add(websocket)
        
        # Clean up disconnected clients
        self.trade_subscribers -= disconnected
    
    async def broadcast_book_update(self, book: OrderBook):
        """Broadcast order book update to all subscribers"""
        if not self.book_subscribers:
            return
        
        message = json.dumps({
            'type': 'orderbook',
            'data': book.get_depth(20)
        })
        
        # Send to all book subscribers
        disconnected = set()
        for websocket in self.book_subscribers:
            try:
                await websocket.send(message)
            except websockets.exceptions.ConnectionClosed:
                disconnected.add(websocket)
        
        # Clean up disconnected clients
        self.book_subscribers -= disconnected
    
    def on_trade(self, trade: Trade):
        """Callback for new trades"""
        asyncio.create_task(self.broadcast_trade(trade))
    
    def on_book_update(self, book: OrderBook):
        """Callback for order book updates"""
        asyncio.create_task(self.broadcast_book_update(book))