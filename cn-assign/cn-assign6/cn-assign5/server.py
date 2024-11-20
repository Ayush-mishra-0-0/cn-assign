import asyncio
import websockets
import os
import threading
import logging
from datetime import datetime

class CollaborativeServer:
    def __init__(self):
        self.clients = set()
        self.document = ""
        self.mutex = threading.Lock()
        
        # Setup logging with more detailed format
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        self.logger = logging.getLogger('CollaborativeServer')
        
        # Ensure temp directory exists
        self.temp_dir = 'temp'
        os.makedirs(self.temp_dir, exist_ok=True)
        
        # Create new file with timestamp
        self.filename = os.path.join(self.temp_dir, f'document_{datetime.now().strftime("%Y%m%d_%H%M%S")}.txt')
        self.load_or_create_document()

    def load_or_create_document(self):
        """Initialize or load the document with proper error handling"""
        try:
            if not os.path.exists(self.filename):
                with open(self.filename, 'w', encoding='utf-8') as f:
                    f.write("")
            with open(self.filename, 'r', encoding='utf-8') as f:
                self.document = f.read()
            self.logger.info(f"Document loaded successfully: {self.filename}")
        except Exception as e:
            self.logger.error(f"Error handling document file: {str(e)}")
            raise

    async def register(self, websocket):
        """Register a new client with connection limits and logging"""
        client_address = websocket.remote_address
        if len(self.clients) >= 10:
            self.logger.warning(f"Rejected connection from {client_address}: server full")
            await websocket.close(1013, "Server full")  # 1013 is "Try Again Later"
            return False
        
        self.clients.add(websocket)
        self.logger.info(f"New client connected: {client_address}. Total clients: {len(self.clients)}")
        return True

    async def unregister(self, websocket):
        """Unregister a client with proper cleanup"""
        if websocket in self.clients:
            self.clients.remove(websocket)
            self.logger.info(f"Client {websocket.remote_address} disconnected. Remaining clients: {len(self.clients)}")

    def save_document(self, content):
        """Save document with error handling"""
        try:
            with open(self.filename, 'w', encoding='utf-8') as f:
                f.write(content)
        except Exception as e:
            self.logger.error(f"Error saving document: {str(e)}")
            raise

    async def handle_client(self, websocket, path):
        """Handle individual client connections with improved error handling"""
        if not await self.register(websocket):
            return

        try:
            # Send current document state
            await websocket.send(self.document)
            
            # Handle incoming messages
            async for message in websocket:
                if not message:  # Skip empty messages
                    continue
                    
                with self.mutex:
                    self.document = message
                    
                    # Save to file
                    try:
                        self.save_document(message)
                    except Exception as e:
                        self.logger.error(f"Failed to save document: {str(e)}")
                        continue
                    
                    self.logger.info(f"Update from {websocket.remote_address}: {message[:50]}...")
                    await self.broadcast(websocket, message)
                    
        except websockets.exceptions.ConnectionClosed as e:
            self.logger.info(f"Client {websocket.remote_address} connection closed: {str(e)}")
        except Exception as e:
            self.logger.error(f"Error handling client {websocket.remote_address}: {str(e)}")
        finally:
            await self.unregister(websocket)

    async def broadcast(self, sender, message):
        """Broadcast updates with error handling"""
        if not self.clients:
            return

        disconnected_clients = set()
        for client in self.clients:
            if client != sender and client.open:
                try:
                    await client.send(message)
                except websockets.exceptions.ConnectionClosed:
                    disconnected_clients.add(client)
                except Exception as e:
                    self.logger.error(f"Error broadcasting to {client.remote_address}: {str(e)}")
                    disconnected_clients.add(client)
        
        # Clean up disconnected clients
        for client in disconnected_clients:
            await self.unregister(client)

async def main():
    server = CollaborativeServer()
    
    print(f"Server starting on ws://localhost:8080")
    
    async with websockets.serve(
        server.handle_client, 
        "localhost", 
        8080,
        ping_interval=20,  # Send ping every 20 seconds
        ping_timeout=30,   # Wait 30 seconds for pong response
        max_size=1024 * 1024  # 1MB max message size
    ):
        await asyncio.Future()  # run forever

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nServer shutting down gracefully...")
    except Exception as e:
        logging.error(f"Fatal server error: {str(e)}")
        raise