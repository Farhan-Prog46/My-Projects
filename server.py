import socket
import threading
from datetime import datetime

from Database import init_db, create_user, authenticate_user, store_message

HOST = socket.gethostbyname(socket.gethostname())
PORT = 5050
MAX_CONNECTIONS = 10

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind((HOST, PORT))
server.listen(MAX_CONNECTIONS)

# list of (conn, username)
clients = []
clients_lock = threading.Lock()

def broadcast(message: str) -> None:
    """Send a text message to all connected clients."""
    data = message.encode("utf-8")
    with clients_lock:
        for conn, _ in clients:
            try:
                conn.sendall(data)
            except OSError:
                # ignore broken connections
                pass

def handle_client(conn: socket.socket, addr) -> None:
    """Handle login/registration and chat for a single client."""
    print(f"[NEW CONNECTION] {addr} connected.")
    username = None
    authenticated = False

    try:
        # -------- LOGIN / REGISTER LOOP --------
        while not authenticated:
            data = conn.recv(1024)
            if not data:
                print(f"[DISCONNECT BEFORE LOGIN] {addr}")
                conn.close()
                return

            message = data.decode("utf-8").strip()
            parts = message.split("|")
            command = parts[0] if parts else ""

            # REGISTER|email|username|password
            if command == "REGISTER" and len(parts) == 4:
                email = parts[1]
                username_try = parts[2]
                password = parts[3]

                success = create_user(email, username_try, password)
                if success:
                    conn.sendall(
                        "REGISTER_OK|Account created successfully. Please log in.\n"
                        .encode("utf-8")
                    )
                else:
                    conn.sendall(
                        "REGISTER_FAIL|Email or username already exists.\n"
                        .encode("utf-8")
                    )

            # LOGIN|username|password
            elif command == "LOGIN" and len(parts) == 3:
                username_try = parts[1]
                password = parts[2]

                if authenticate_user(username_try, password):
                    username = username_try
                    authenticated = True
                    conn.sendall("LOGIN_OK|Login successful.\n".encode("utf-8"))
                else:
                    conn.sendall(
                        "LOGIN_FAIL|Invalid username or password.\n".encode("utf-8")
                    )
            else:
                conn.sendall(
                    "ERROR|Invalid command. Use LOGIN or REGISTER.\n".encode("utf-8")
                )

        # -------- ADD CLIENT TO LIST --------
        with clients_lock:
            clients.append((conn, username))

        join_msg = f"[SYSTEM] {username} joined the chat.\n"
        print(join_msg.strip())
        broadcast(join_msg)

        # -------- CHAT LOOP --------
        while True:
            data = conn.recv(1024)
            if not data:
                break  # client disconnected

            message = data.decode("utf-8").strip()

            # normal chat message: MSG|text
            if message.startswith("MSG|"):
                text = message[4:].strip()
                if text:
                    # store in DB
                    store_message(username, text)
                    # broadcast
                    timestamp = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
                    chat_line = f"[{timestamp}] {username}: {text}\n"
                    broadcast(chat_line)
                continue

    except Exception as exc:
        print(f"[ERROR] Problem with client {addr}: {exc}")

    finally:
        # remove from clients list
        with clients_lock:
            clients[:] = [(c, u) for (c, u) in clients if c is not conn]

        try:
            conn.close()
        except OSError:
            pass

        if username:
            leave_msg = f"[SYSTEM] {username} left the chat.\n"
            print(leave_msg.strip())
            broadcast(leave_msg)

        print(f"[CONNECTION CLOSED] {addr}")

def start_server() -> None:
    """Initialize DB and start the TCP server."""
    init_db()
    print(f"[SERVER STARTED] Listening on {HOST}:{PORT}")

    try:
        while True:
            conn, addr = server.accept()
            thread = threading.Thread(
                target=handle_client,
                args=(conn, addr),
                daemon=True,
            )
            thread.start()
    except KeyboardInterrupt:
        print("\n[SERVER SHUTDOWN] Graceful exit.")

if __name__ == "__main__":
    start_server()
