"""
Main Server
Starts the matching engine with REST and WebSocket servers
"""
import asyncio
import logging
import uvicorn
from threading import Thread
from engine.machine_engine import MatchingEngine
from api.rest_api import create_rest_api
from api.websocket_server import WebSocketServer

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('matching_engine.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Create app instance for uvicorn
matching_engine = MatchingEngine()
app = create_rest_api(matching_engine)

class Server:
    """Main server coordinating all components"""
    def __init__(self, rest_host='0.0.0.0', rest_port=8000, ws_host='0.0.0.0', ws_port=8765):
        self.rest_host = rest_host
        self.rest_port = rest_port
        self.ws_host = ws_host
        self.ws_port = ws_port
        
        # Initialize matching engine
        self.matching_engine = MatchingEngine()
        
        # Initialize WebSocket server
        self.ws_server = WebSocketServer(ws_host, ws_port)
        
        # Register callbacks
        self.matching_engine.register_trade_callback(self.ws_server.on_trade)
        self.matching_engine.register_book_update_callback(self.ws_server.on_book_update)
        
        # Create REST API
        self.rest_app = create_rest_api(self.matching_engine)
        
        logger.info("Server initialized")
    
    def run_rest_api(self):
        """Run REST API server"""
        uvicorn.run(
            self.rest_app,
            host=self.rest_host,
            port=self.rest_port,
            log_level="info"
        )
    
    async def run_websocket_server(self):
        """Run WebSocket server"""
        await self.ws_server.start()
    
    def start(self):
        """Start all servers"""
        logger.info("Starting matching engine servers...")
        
        # Start REST API in a separate thread
        rest_thread = Thread(target=self.run_rest_api, daemon=True)
        rest_thread.start()
        
        # Start WebSocket server in main thread
        try:
            asyncio.run(self.run_websocket_server())
        except KeyboardInterrupt:
            logger.info("Shutting down servers...")

def main():
    """Main entry point"""
    server = Server(
        rest_host='0.0.0.0',
        rest_port=8000,
        ws_host='0.0.0.0',
        ws_port=8765
    )
    
    logger.info("=" * 60)
    logger.info("Cryptocurrency Matching Engine")
    logger.info("=" * 60)
    logger.info(f"REST API: http://localhost:8000")
    logger.info(f"WebSocket: ws://localhost:8765")
    logger.info(f"API Docs: http://localhost:8000/docs")
    logger.info("=" * 60)
    
    server.start()

if __name__ == "__main__":
    main()