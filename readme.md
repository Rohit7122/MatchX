# MatchX Trading Platform

A high-performance cryptocurrency trading platform with a matching engine backend and real-time trading interface.



## System Architecture

- **Backend**: Python-based matching engine with REST API and WebSocket server
- **Frontend**: Next.js web application with real-time market data visualization

## Prerequisites

### Backend
- Python 3.8+
- pip (Python package manager)

### Frontend
- Node.js 18+
- npm (Node package manager)

## Quick Start

### Backend Setup
```sh
# Navigate to backend directory
cd backend

# Create and activate virtual environment
python -m venv venv
source venv/bin/activate  # For Mac/Linux

# Install dependencies
pip install -r requirements.txt

# Start the server
python -m uvicorn main:app --reload
```

### Frontend Setup
```sh
# Navigate to frontend directory
cd frontend

# Install dependencies
npm install

# Start development server
npm run dev
```

## Available Services

### Backend Endpoints
- REST API: http://localhost:8000
- WebSocket: ws://localhost:8765
- API Documentation: http://localhost:8000/docs

### Frontend Access
- Trading Interface: http://localhost:3000

## Core Features

### Backend
- Price-Time Priority Matching
- Multiple Order Types (Market, Limit, IOC, FOK)
- Real-time Market Data Feed
- RESTful API for Order Management
- WebSocket Integration

### Frontend
- Real-time Order Book Visualization
- Live Trade History
- Market Data Charts
- Dark Mode Interface
- Responsive Design

## Development Stack

### Backend
- FastAPI for REST API
- asyncio for WebSocket server
- uvicorn ASGI server
- Comprehensive logging system

### Frontend
- Next.js and TypeScript
- TailwindCSS for styling
- Real-time WebSocket integration
- Component-based architecture

## Logging

Backend logs are available in:
- Console output
- `matching_engine.log` file

## API Documentation

Visit http://localhost:8000/docs after starting the backend server for interactive API documentation.


