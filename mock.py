import socket
import select
import json

# Telnet command codes
IAC = 255   # Interpret As Command
DONT = 254
DO = 253
WONT = 252
WILL = 251
SB = 250    # Subnegotiation Begin
SE = 240    # Subnegotiation End
GMCP = 201  # Generic MUD Communication Protocol

def send_gmcp_message(sock, message, data=""):
    """Send a GMCP message to a client."""
    msg = f"{message} {json.dumps(data)}" if data else message
    # GMCP data needs to be wrapped in IAC SB GMCP <data> IAC SE
    gmcp_data = IAC.to_bytes(1, 'big') + SB.to_bytes(1, 'big') + GMCP.to_bytes(1, 'big') + msg.encode() + IAC.to_bytes(1, 'big') + SE.to_bytes(1, 'big')
    sock.send(gmcp_data)

def negotiate_gmcp(sock):
    """Negotiate GMCP with the client."""
    sock.send(IAC.to_bytes(1, 'big') + WILL.to_bytes(1, 'big') + GMCP.to_bytes(1, 'big'))

def parse_telnet_commands(data, sock):
    """Parse telnet commands and respond accordingly."""
    if data[0] == IAC and data[1] == DO and data[2] == GMCP:
        print("Client supports GMCP.")
    elif data[0] == IAC and data[1] in (DO, DONT, WILL, WONT):
        # Respond to other negotiations as needed
        pass
    else:
        # Handle other data/commands
        pass

def main():
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server_socket.bind(('0.0.0.0', 2003)) 
    server_socket.listen()

    print("Telnet server started on port 2003.")

    clients = []

    try:
        while True:
            read_sockets, _, _ = select.select([server_socket] + clients, [], [])

            for sock in read_sockets:
                if sock == server_socket:
                    client_socket, client_address = server_socket.accept()
                    print(f"Client {client_address} connected.")
                    clients.append(client_socket)
                    negotiate_gmcp(client_socket)
                else:
                    try:
                        data = sock.recv(1024)
                        if data:
                            parse_telnet_commands(data, sock)
                        else:
                            print("Client disconnected.")
                            clients.remove(sock)
                            sock.close()
                    except Exception as e:
                        print(f"Error: {e}")
                        clients.remove(sock)
                        sock.close()
    except KeyboardInterrupt:
        print("Server shutting down.")
    finally:
        server_socket.close()

if __name__ == "__main__":
    main()
