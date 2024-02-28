import socket
import select
import json

# Constants for Telnet commands and GMCP
IAC = 255
SB = 250
SE = 240
WILL = 251
DO = 253
DONT = 254
WONT = 252
GMCP = 201


# Helper function to send GMCP messages
def send_gmcp(sock, message, data):
    gmcp_data = f"{message} {json.dumps(data)}"
    sock.send(bytes([IAC, SB, GMCP]) + gmcp_data.encode("utf-8") + bytes([IAC, SE]))

def send_text(sock, message):
    sock.send(message.encode("utf-8"))

def process_data(sock, data):
    # Remove GMCP acknowledgement from the message
    if bytes([IAC, DO, GMCP]) in data:
        data = data.replace(bytes([IAC, DO, GMCP]), b"")

    # Simple parsing for GMCP data (intened for mock only)
    if not (
        data.startswith(bytes([IAC, SB, GMCP])) and data.endswith(bytes([IAC, SE]))
    ):
        print(f"Received non GMCP data: {data}")

        # emulate a traditional login
        if b"hunter2" in data:
            send_text(sock, "Traditional login successful.")

        return
    else:
        data = data.replace(bytes([IAC, SB, GMCP]), b"")
        data = data.replace(bytes([IAC, SB]), b"")

        gmcp_messages = data.split(bytes([IAC, SE]))
        for message in gmcp_messages:
            if not message:
                continue

            message = message.decode("utf-8")
            print(f"Received GMCP message: {message}")

            try:
                # Load GMCP message as JSON
                parts = message.split(" ", 1)
                if not len(parts) >= 2:
                     continue

                gmcp_json = gmcp_json = json.loads(parts[1])
                if "Char.Login 1" in gmcp_json:
                    send_gmcp(
                        sock,
                        "Char.Login.Default",
                        {"type": ["password-credentials"]},
                    )

                if "Char.Login.Credentials" in message:
                    credentials = gmcp_json

                    if credentials["account"] == "admin" and credentials["password"] == "hunter2":
                        send_gmcp(sock, "Char.Login.Result", {"success": True})
                        send_text(sock, "Authentication successful. Welcome to the server!")
                        print("Authentication successful")
                        return
                    else:
                        send_gmcp(
                            sock,
                            "Char.Login.Result",
                            {"success": False, "message": "Invalid credentials"},
                        )
                        send_text(sock, "GMCP Authentication flow was successful, but the credentials were incorrect.")
                        print("Authentication failed")
            except json.JSONDecodeError:
                print("Error decoding GMCP JSON")


# Main server function
def start_server(host="0.0.0.0", port=2003):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server_sock:
        server_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        server_sock.bind((host, port))
        server_sock.listen()
        print(f"Server listening on {host}:{port}")

        connected_clients = []

        try:
            while True:
                readable, _, _ = select.select(
                    [server_sock] + connected_clients, [], []
                )
                for sock in readable:
                    if sock is server_sock:
                        client_sock, client_address = server_sock.accept()
                        print(f"Connection from {client_address}")
                        connected_clients.append(client_sock)

                        # Negotiate GMCP
                        client_sock.send(b"Welcome to the server!\n")
                        client_sock.send(bytes([IAC, WILL, GMCP]))
                    else:
                        data = sock.recv(1024)
                        if not data:
                            print(f"Client {sock.getpeername()} disconnected")
                            connected_clients.remove(sock)
                            sock.close()
                        else:
                            process_data(sock, data)
        except KeyboardInterrupt:
            print("Server shutting down")


if __name__ == "__main__":
    start_server()
