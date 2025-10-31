"""
REST API
HTTP endpoints for order submission and data retrieval
"""
from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field, validator
from typing import Optional, List
from decimal import Decimal
import logging

from engine.machine_engine import MatchingEngine
from engine.order import Order

logger = logging.getLogger(__name__)

# Pydantic models for request validation
class OrderRequest(BaseModel):
    symbol: str = Field(..., description="Trading pair symbol", example="BTC-USDT")
    order_type: str = Field(..., description="Order type", example="limit")
    side: str = Field(..., description="Order side", example="buy")
    quantity: float = Field(..., gt=0, description="Order quantity", example=1.5)
    price: Optional[float] = Field(None, gt=0, description="Order price", example=50000.0)
    
    @validator('order_type')
    def validate_order_type(cls, v):
        valid_types = ['market', 'limit', 'ioc', 'fok']
        if v.lower() not in valid_types:
            raise ValueError(f'order_type must be one of {valid_types}')
        return v.lower()
    
    @validator('side')
    def validate_side(cls, v):
        if v.lower() not in ['buy', 'sell']:
            raise ValueError('side must be "buy" or "sell"')
        return v.lower()

class CancelOrderRequest(BaseModel):
    symbol: str = Field(..., description="Trading pair symbol")
    order_id: str = Field(..., description="Order ID to cancel")

def create_rest_api(matching_engine: MatchingEngine) -> FastAPI:
    """Create FastAPI application with matching engine"""
    
    app = FastAPI(
        title="Cryptocurrency Matching Engine API",
        description="REG NMS-inspired high-performance matching engine",
        version="1.0.0"
    )
    
    # CORS middleware for frontend
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],  # Configure appropriately for production
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    @app.get("/")
    async def root():
        """API root"""
        return {
            "name": "Cryptocurrency Matching Engine",
            "version": "1.0.0",
            "status": "running"
        }
    
    @app.get("/health")
    async def health_check():
        """Health check endpoint"""
        return {"status": "healthy"}
    
    @app.post("/api/orders")
    async def submit_order(order_request: OrderRequest):
        """
        Submit a new order to the matching engine
        
        - **symbol**: Trading pair (e.g., BTC-USDT)
        - **order_type**: market, limit, ioc, or fok
        - **side**: buy or sell
        - **quantity**: Amount to trade
        - **price**: Limit price (required for limit, ioc, fok orders)
        """
        try:
            # Create order
            order = Order.create_order(
                symbol=order_request.symbol,
                order_type=order_request.order_type,
                side=order_request.side,
                quantity=order_request.quantity,
                price=order_request.price
            )
            
            # Submit to matching engine
            result = matching_engine.submit_order(order)
            
            return result
            
        except ValueError as e:
            logger.error(f"Invalid order: {e}")
            raise HTTPException(status_code=400, detail=str(e))
        except Exception as e:
            logger.error(f"Error submitting order: {e}", exc_info=True)
            raise HTTPException(status_code=500, detail="Internal server error")
    
    @app.delete("/api/orders")
    async def cancel_order(cancel_request: CancelOrderRequest):
        """
        Cancel an existing order
        
        - **symbol**: Trading pair
        - **order_id**: ID of the order to cancel
        """
        try:
            result = matching_engine.cancel_order(
                symbol=cancel_request.symbol,
                order_id=cancel_request.order_id
            )
            
            if not result['success']:
                raise HTTPException(status_code=404, detail=result['message'])
            
            return result
            
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error cancelling order: {e}", exc_info=True)
            raise HTTPException(status_code=500, detail="Internal server error")
    
    @app.get("/api/orderbook/{symbol}")
    async def get_order_book(symbol: str, depth: int = 10):
        """
        Get current order book for a symbol
        
        - **symbol**: Trading pair (e.g., BTC-USDT)
        - **depth**: Number of price levels to return (default: 10)
        """
        try:
            if depth < 1 or depth > 100:
                raise HTTPException(status_code=400, detail="Depth must be between 1 and 100")
            
            book = matching_engine.get_order_book(symbol.upper(), depth)
            return book
            
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error fetching order book: {e}", exc_info=True)
            raise HTTPException(status_code=500, detail="Internal server error")
    
    @app.get("/api/bbo/{symbol}")
    async def get_bbo(symbol: str):
        """
        Get Best Bid and Offer for a symbol
        
        - **symbol**: Trading pair (e.g., BTC-USDT)
        """
        try:
            bbo = matching_engine.get_bbo(symbol.upper())
            return bbo
            
        except Exception as e:
            logger.error(f"Error fetching BBO: {e}", exc_info=True)
            raise HTTPException(status_code=500, detail="Internal server error")
    
    @app.get("/api/trades")
    async def get_recent_trades(symbol: Optional[str] = None, limit: int = 50):
        """
        Get recent trades
        
        - **symbol**: Filter by trading pair (optional)
        - **limit**: Number of trades to return (default: 50, max: 200)
        """
        try:
            if limit < 1 or limit > 200:
                raise HTTPException(status_code=400, detail="Limit must be between 1 and 200")
            
            trades = matching_engine.trades[-limit:]
            
            if symbol:
                trades = [t for t in trades if t.symbol == symbol.upper()]
            
            return {
                "trades": [t.to_dict() for t in reversed(trades)],
                "count": len(trades)
            }
            
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error fetching trades: {e}", exc_info=True)
            raise HTTPException(status_code=500, detail="Internal server error")
    
    @app.get("/api/symbols")
    async def get_symbols():
        """Get all active trading symbols"""
        try:
            symbols = list(matching_engine.books.keys())
            return {
                "symbols": symbols,
                "count": len(symbols)
            }
        except Exception as e:
            logger.error(f"Error fetching symbols: {e}", exc_info=True)
            raise HTTPException(status_code=500, detail="Internal server error")
    
    return app