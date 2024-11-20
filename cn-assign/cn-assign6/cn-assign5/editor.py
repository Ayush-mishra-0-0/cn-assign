# server.py
import socket
import threading
import os

class CollaborativeServer:
    def __init__(self, host='localhost', port=8080):
        self.host = host
        self.port = port
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.clients = []  # List to store client connections
        self.document = ""  # Shared document content
        self.mutex = threading.Lock()  # Mutex for synchronization
        
        # Create or open temp.txt
        try:
            if not os.path.exists('temp.txt'):
                with open('temp.txt', 'w') as f:
                    f.write("")
            # Load existing content
            with open('temp.txt', 'r') as f:
                self.document = f.read()
        except Exception as e:
            print("Error opening file temp.txt")
            raise e

    def start(self):
        """Start the server and listen for connections"""
        try:
            self.server_socket.bind((self.host, self.port))
            self.server_socket.listen(10)
            print(f"Server listening on port {self.port}")
            
            while True:
                client_socket, address = self.server_socket.accept()
                if len(self.clients) < 10:
                    client_thread = threading.Thread(
                        target=self.handle_client,
                        args=(client_socket, address)
                    )
                    self.clients.append({
                        'socket': client_socket,
                        'address': address
                    })
                    print(f"New client connected: {address}")
                    client_thread.start()
                else:
                    client_socket.send("Server is full".encode())
                    client_socket.close()
        except Exception as e:
            print(f"Server error: {e}")
        finally:
            self.server_socket.close()

    def handle_client(self, client_socket, address):
        """Handle individual client connections"""
        try:
            # Send current document state to new client
            with self.mutex:
                client_socket.send(self.document.encode())
            
            while True:
                update = client_socket.recv(1024).decode()
                if not update:
                    break
                
                with self.mutex:
                    # Update document in memory
                    self.document = update
                    
                    # Append to temp.txt
                    try:
                        with open('temp.txt', 'a') as f:
                            f.write(update + "\n")
                    except Exception as e:
                        print(f"Error writing to temp.txt: {e}")
                    
                    print(f"Received update from client {address}: {update}")
                    print("Broadcasting update to all clients")
                    
                    # Broadcast to all other clients
                    self.broadcast_update(client_socket, update)
        
        except Exception as e:
            print(f"Error handling client {address}: {e}")
        finally:
            # Clean up on client disconnect
            for client in self.clients:
                if client['socket'] == client_socket:
                    self.clients.remove(client)
                    break
            client_socket.close()
            print(f"Client {address} disconnected")

    def broadcast_update(self, sender_socket, update):
        """Broadcast updates to all clients except sender"""
        for client in self.clients:
            if client['socket'] != sender_socket:
                try:
                    client['socket'].send(update.encode())
                except:
                    # Remove dead connections
                    self.clients.remove(client)
                    client['socket'].close()

# client.py
class CollaborativeClient:
    def __init__(self, host='localhost', port=8080):
        self.host = host
        self.port = port
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        
    def start(self):
        """Start the client and connect to server"""
        try:
            self.socket.connect((self.host, self.port))
            print("Connected to the server. Start typing to edit the document:")
            
            # Start thread for receiving updates
            receive_thread = threading.Thread(target=self.receive_updates)
            receive_thread.daemon = True
            receive_thread.start()
            
            # Handle user input in main thread
            self.handle_user_input()
            
        except Exception as e:
            print(f"Error connecting to server: {e}")
        finally:
            self.socket.close()

    def receive_updates(self):
        """Receive updates from the server"""
        try:
            while True:
                update = self.socket.recv(1024).decode()
                if not update:
                    break
                print(f"\nDocument updated: {update}")
                print("Enter your edit (or 'quit' to exit): ", end='', flush=True)
        except:
            print("\nDisconnected from server")
        finally:
            self.socket.close()

    def handle_user_input(self):
        """Handle user input and send updates"""
        try:
            while True:
                user_input = input()
                if user_input.lower() == 'quit':
                    break
                
                # Send update to server
                self.socket.send(user_input.encode())
                
        except Exception as e:
            print(f"Error sending update: {e}")
        finally:
            self.socket.close()

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "server":
        server = CollaborativeServer()
        server.start()
    else:
        client = CollaborativeClient()
        client.start()