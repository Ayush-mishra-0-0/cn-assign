# server.py
import socket
import threading
import json
import time

class CollaborativeServer:
    def __init__(self, host='localhost', port=5000):
        self.host = host
        self.port = port
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.clients = []  # List to store client connections
        self.document = ""  # Shared document content
        self.lock = threading.Lock()  # Lock for thread synchronization
        
    def start(self):
        """Start the server and listen for connections"""
        self.server_socket.bind((self.host, self.port))
        self.server_socket.listen(10)  # Allow up to 10 clients
        print(f"Server started on {self.host}:{self.port}")
        
        # Load existing document if it exists
        try:
            with open('temp.txt', 'r') as f:
                self.document = f.read()
        except FileNotFoundError:
            pass
            
        while True:
            client_socket, address = self.server_socket.accept()
            print(f"New connection from {address}")
            
            if len(self.clients) < 10:
                client_thread = threading.Thread(
                    target=self.handle_client,
                    args=(client_socket, address)
                )
                self.clients.append(client_socket)
                client_thread.start()
            else:
                client_socket.send("Server is full".encode())
                client_socket.close()
    
    def handle_client(self, client_socket, address):
        """Handle individual client connections"""
        # Send current document state to new client
        self.send_document_state(client_socket)
        
        try:
            while True:
                data = client_socket.recv(1024).decode()
                if not data:
                    break
                    
                # Handle received updates
                with self.lock:
                    update = json.loads(data)
                    self.document = update['content']
                    
                    # Save to file
                    with open('temp.txt', 'w') as f:
                        f.write(self.document)
                    
                    # Broadcast to all other clients
                    self.broadcast_update(client_socket, update)
                    
                print(f"Update received from {address}: {update}")
                
        except Exception as e:
            print(f"Error handling client {address}: {e}")
        finally:
            self.clients.remove(client_socket)
            client_socket.close()
            print(f"Connection closed with {address}")
    
    def send_document_state(self, client_socket):
        """Send current document state to a client"""
        state = {
            'type': 'full_state',
            'content': self.document
        }
        client_socket.send(json.dumps(state).encode())
    
    def broadcast_update(self, sender_socket, update):
        """Broadcast updates to all clients except sender"""
        for client in self.clients:
            if client != sender_socket:
                try:
                    client.send(json.dumps(update).encode())
                except:
                    self.clients.remove(client)
                    client.close()

if __name__ == "__main__":
    server = CollaborativeServer()
    server.start()
