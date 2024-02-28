# Mock MUD Server

This is a mock MUD server implementation that demonstrates [GMCP Authentication](https://wiki.mudlet.org/w/Standards:GMCP_Authentication) support.

## Overview

- The actual implementation relevant to the spec is in a few lines of Python: https://github.com/vadi2/gmcp-auth-mock/blob/main/mock.py#L53-L77

## Usage

To start the server:

```bash
python mock.py
```

By default it will listen on `localhost:2003`.

To connect:

- Use a MUD client that supports GMCP Auth
- Connect to the server on port `2003`
- The server will initiate GMCP negotiation
- Send credentials in the GMCP authentication flow:
  - Account: `admin`
  - Password: `hunter2`

The server will also accept a plain text password of `hunter2`.

## Implementation Details

- `start_server()` contains the main server loop
- `send_gmcp()` helper to send GMCP messages
- `send_text()` helper to send plain text
- `process_data()` parses incoming data and handles GMCP

The server listens for connections in a loop. When data is received:

- GMCP messages are parsed from the telnet data
- On `Char.Login` messages, the credentials are checked
- Responses are sent over GMCP and plain text

This shows a basic GMCP implementation and authentication flow.

## License

MIT
