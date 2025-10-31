"""
Trade Model
Represents executed trades in the matching engine
"""
from dataclasses import dataclass
from decimal import Decimal
from datetime import datetime
from typing import Optional
import uuid

@dataclass
class Trade:
    """Represents an executed trade"""
    trade_id: str
    symbol: str
    price: Decimal
    quantity: Decimal
    timestamp: datetime
    aggressor_side: str  # 'buy' or 'sell' - the side that initiated
    maker_order_id: str  # The resting order
    taker_order_id: str  # The incoming order
    
    @staticmethod
    def create_trade(symbol: str, price: Decimal, quantity: Decimal,
                    aggressor_side: str, maker_order_id: str, 
                    taker_order_id: str) -> 'Trade':
        """Factory method to create a trade"""
        return Trade(
            trade_id=str(uuid.uuid4()),
            symbol=symbol,
            price=price,
            quantity=quantity,
            timestamp=datetime.utcnow(),
            aggressor_side=aggressor_side,
            maker_order_id=maker_order_id,
            taker_order_id=taker_order_id
        )
    
    def to_dict(self) -> dict:
        """Convert trade to dictionary for JSON serialization"""
        return {
            'trade_id': self.trade_id,
            'symbol': self.symbol,
            'price': str(self.price),
            'quantity': str(self.quantity),
            'timestamp': self.timestamp.isoformat() + 'Z',
            'aggressor_side': self.aggressor_side,
            'maker_order_id': self.maker_order_id,
            'taker_order_id': self.taker_order_id
        }