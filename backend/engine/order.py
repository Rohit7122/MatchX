"""
Order Model
Represents different order types in the matching engine
"""
from enum import Enum
from dataclasses import dataclass
from decimal import Decimal
from datetime import datetime
from typing import Optional
import uuid

class OrderType(Enum):
    MARKET = "market"
    LIMIT = "limit"
    IOC = "ioc"  # Immediate-Or-Cancel
    FOK = "fok"  # Fill-Or-Kill

class OrderSide(Enum):
    BUY = "buy"
    SELL = "sell"

class OrderStatus(Enum):
    PENDING = "pending"
    PARTIAL = "partial"
    FILLED = "filled"
    CANCELLED = "cancelled"
    REJECTED = "rejected"

@dataclass
class Order:
    """Represents a trading order"""
    order_id: str
    symbol: str
    order_type: OrderType
    side: OrderSide
    quantity: Decimal
    price: Optional[Decimal]
    timestamp: datetime
    status: OrderStatus = OrderStatus.PENDING
    filled_quantity: Decimal = Decimal('0')
    remaining_quantity: Decimal = None
    
    def __post_init__(self):
        if self.remaining_quantity is None:
            self.remaining_quantity = self.quantity
            
        # Validate order
        if self.quantity <= 0:
            raise ValueError("Order quantity must be positive")
        
        if self.order_type in [OrderType.LIMIT, OrderType.IOC, OrderType.FOK]:
            if self.price is None or self.price <= 0:
                raise ValueError(f"{self.order_type.value} orders require a positive price")
    
    @staticmethod
    def create_order(symbol: str, order_type: str, side: str, 
                    quantity: float, price: Optional[float] = None) -> 'Order':
        """Factory method to create an order with validation"""
        try:
            order_type_enum = OrderType(order_type.lower())
            side_enum = OrderSide(side.lower())
        except ValueError as e:
            raise ValueError(f"Invalid order type or side: {e}")
        
        return Order(
            order_id=str(uuid.uuid4()),
            symbol=symbol.upper(),
            order_type=order_type_enum,
            side=side_enum,
            quantity=Decimal(str(quantity)),
            price=Decimal(str(price)) if price is not None else None,
            timestamp=datetime.utcnow()
        )
    
    def to_dict(self) -> dict:
        """Convert order to dictionary for JSON serialization"""
        return {
            'order_id': self.order_id,
            'symbol': self.symbol,
            'order_type': self.order_type.value,
            'side': self.side.value,
            'quantity': str(self.quantity),
            'price': str(self.price) if self.price else None,
            'timestamp': self.timestamp.isoformat() + 'Z',
            'status': self.status.value,
            'filled_quantity': str(self.filled_quantity),
            'remaining_quantity': str(self.remaining_quantity)
        }
    
    def is_marketable(self, best_bid: Optional[Decimal], 
                     best_ask: Optional[Decimal]) -> bool:
        """Check if order can be immediately matched"""
        if self.order_type == OrderType.MARKET:
            return True
        
        if self.side == OrderSide.BUY:
            return best_ask is not None and self.price >= best_ask
        else:
            return best_bid is not None and self.price <= best_bid