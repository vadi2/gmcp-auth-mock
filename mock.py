import json
import socket
import threading

class TelnetServer:
    def __init__(self, host='0.0.0.0', port=2003):
        self.host = host
        self.port = port
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.clients = []

    def start_server(self):
        self.server_socket.bind((self.host, self.port))
        self.server_socket.listen()
        print(f'Server started on {self.host}:{self.port}')
        try:
            while True:
                client_socket, client_address = self.server_socket.accept()
                print(f'Client connected: {client_address}')
                client_thread = threading.Thread(target=self.handle_client, args=(client_socket,))
                client_thread.start()
        except KeyboardInterrupt:
            print('Server shutting down...')
        finally:
            self.server_socket.close()

    def handle_client(self, client_socket):
        try:
            while True:
                data = client_socket.recv(1024)
                if not data:
                    break
                message = data.decode('utf-8')
                self.process_message(message, client_socket)
        except ConnectionResetError:
            print('Client disconnected')
        finally:
            client_socket.close()

    def process_message(self, message, client_socket):
        try:
            # Simulating processing of GMCP messages
            if 'Client.Supports.Set' in message:
                supported_auth_methods = json.dumps({
                    "Client.Authenticate.Default": {"type": ["password-credentials"]}
                })
                client_socket.send(supported_auth_methods.encode('utf-8'))
            elif 'Client.Authenticate.Credentials' in message:
                # Simplified credential check (replace with real validation logic)
                credentials = json.loads(message.split(' ', 1)[1])
                username = credentials.get('character')
                password = credentials.get('password')
                if username == "username" and password == "password":  # Placeholder check
                    auth_result = json.dumps({
                        "Client.Authenticate.Result": {"success": True}
                    })
                else:
                    auth_result = json.dumps({
                        "Client.Authenticate.Result": {"success": False, "message": "Invalid credentials"}
                    })
                client_socket.send(auth_result.encode('utf-8'))
        except Exception as e:
            print(f'Error processing message: {e}')

if __name__ == "__main__":
    server = TelnetServer()
    server.start_server()
