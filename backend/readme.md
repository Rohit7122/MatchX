# Cryptocurrency Matching Engine

A high-performance cryptocurrency matching engine implementing REG NMS-inspired price-time priority matching with WebSocket market data feed and REST API.

## Features

- **Price-Time Priority Matching**: Fair and deterministic order execution
- **Multiple Order Types**:
  - Market Orders
  - Limit Orders
  - IOC (Immediate-or-Cancel)
  - FOK (Fill-or-Kill)
- **Real-time Market Data**: WebSocket feed for trades and order book updates
- **RESTful API**: Comprehensive HTTP endpoints for order management
- **Thread-Safe**: Concurrent order processing with proper locking
- **Logging**: Detailed logging with file and console output

## Prerequisites

- Python 3.8+
- pip (Python package manager)

## Installation

1. Clone the repository:
```sh
git clone <repository-url>
cd <repository-directory>
```

2. Create a virtual environment (recommended):
```sh
python -m venv venv
source venv/bin/activate  # On Windows use: venv\Scripts\activate
```

3. Install dependencies:
```sh
pip install -r requirements.txt
```

## Running the Application

Start the server with hot-reload enabled:

```sh
python -m uvicorn main:app --reload
```

The following services will be available:
- REST API: http://localhost:8000
- WebSocket: ws://localhost:8765
- API Documentation: http://localhost:8000/docs

## API Documentation

### REST Endpoints

- `GET /`: Root endpoint with service information
- `GET /health`: Health check endpoint
- `POST /api/orders`: Submit new order
- `DELETE /api/orders`: Cancel existing order
- `GET /api/orderbook/{symbol}`: Get order book depth
- `GET /api/bbo/{symbol}`: Get best bid and offer
- `GET /api/trades`: Get recent trades
- `GET /api/symbols`: List available trading pairs

### WebSocket Channels

- `trades`: Real-time trade feed
- `orderbook`: Real-time order book updates

## Example Usage

### Submit Limit Order (REST)

```sh
curl -X POST http://localhost:8000/api/orders \
  -H "Content-Type: application/json" \
  -d '{
    "symbol": "BTC-USDT",
    "order_type": "limit",
    "side": "buy",
    "quantity": 1.5,
    "price": 50000.0
  }'
```

### Subscribe to Trade Feed (WebSocket)

```javascript
const ws = new WebSocket('ws://localhost:8765');

ws.onopen = () => {
  ws.send(JSON.stringify({
    action: 'subscribe',
    channel: 'trades'
  }));
};

ws.onmessage = (event) => {
  console.log('Trade:', JSON.parse(event.data));
};
```

## Project Structure

```
├── main.py              # Application entry point
├── requirements.txt     # Python dependencies
├── api/
│   ├── rest_api.py     # REST API implementation
│   └── websocket_server.py # WebSocket server
└── engine/
    ├── machine_engine.py # Matching engine core
    ├── order_book.py    # Order book implementation
    ├── order.py        # Order model
    └── trade.py        # Trade model
```

## Development

The project uses:
- FastAPI for REST API
- WebSockets for real-time data
- SortedContainers for efficient order book operations
- Pydantic for data validation
- Uvicorn as ASGI server

## Logging

Logs are written to:
- Console output
- `matching_engine.log` file