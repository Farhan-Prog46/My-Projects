import socket
import threading

from Database import init_db, create_user, authenticate_user, store_message

HOST = socket.gethostbyname(socket.gethostname())
PORT = 5050
MAX_CONNECTIONS = 10

clients = []  # list of (conn, username)
clients_lock = threading.Lock()


def broadcast(message: str) -> None:
    """Send a text message to all connected clients."""
    data = message.encode("utf-8")
    with clients_lock:
        for conn, _ in clients:
            try:
                conn.sendall(data)
            except OSError:
                # Ignore broken connections here; they will be cleaned up in handler
                pass


def handle_client(conn: socket.socket, addr) -> None:
    """Handle login/registration and chat for a single client."""
    print(f"[NEW CONNECTION] {addr} connected.")
    username = None
    authenticated = False

    try:
        # --------- LOGIN / REGISTER LOOP ----------
        while not authenticated:
            data = conn.recv(1024)
            if not data:
                print(f"[DISCONNECT BEFORE LOGIN] {addr}")
                conn.close()
                return

            message = data.decode("utf-8").strip()
            parts = message.split("|")
            command = parts[0] if parts else ""

            if command == "REGISTER" and len(parts) == 3:
                username_try = parts[1]
                password = parts[2]

                success = create_user(username_try, password)
                if success:
                    conn.sendall(
                        "Account created successfully. Please log in.\n"
                        .encode("utf-8")
                    )
                else:
                    conn.sendall(
                        "Username already exists or could not be created.\n"
                        .encode("utf-8")
                    )

            elif command == "LOGIN" and len(parts) == 3:
                username_try = parts[1]
                password = parts[2]

                if authenticate_user(username_try, password):
                    username = username_try
                    authenticated = True
                    conn.sendall(
                        "Login successful.\n Welcome to the chat.\n"
                        .encode("utf-8")
                    )
                else:
                    conn.sendall(
                        "Invalid username or password.\n".encode("utf-8")
                    )
            else:
                conn.sendall(
                    "Invalid command. Use LOGIN or REGISTER.\n".encode("utf-8")
                )

        # --------- ADD CLIENT TO LIST ----------
        with clients_lock:
            clients.append((conn, username))

        join_msg = f"[SYSTEM] {username} joined the chat.\n"
        print(join_msg.strip())
        broadcast(join_msg)

        # --------- CHAT LOOP ----------
        while True:
            data = conn.recv(1024)
            if not data:
                # Client closed connection
                break

            message = data.decode("utf-8").strip()

            if message == "QUIT":
                break

            if message.startswith("MSG|"):
                text = message[4:].strip()
                if text:
                    # Save in database
                    store_message(username, text)
                    # Broadcast to everyone
                    chat_line = f"{username}: {text}\n"
                    broadcast(chat_line)

    except Exception as exc:
        print(f"[ERROR] Problem with client {addr}: {exc}")
    finally:
        # Remove from clients list
        with clients_lock:
            clients[:] = [(c, u) for (c, u) in clients if c is not conn]

        conn.close()

        if username:
            leave_msg = f"[SYSTEM] {username} left the chat.\n"
            print(leave_msg.strip())
            broadcast(leave_msg)

        print(f"[CONNECTION CLOSED] {addr}")


def start_server() -> None:
    """Initialize DB and start the TCP server."""
    init_db()

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server_socket:
        server_socket.bind((HOST, PORT))
        server_socket.listen(MAX_CONNECTIONS)
        print(f"[STARTED] Chat server listening on {HOST}:{PORT}")

        try:
            while True:
                conn, addr = server_socket.accept()
                thread = threading.Thread(
                    target=handle_client,
                    args=(conn, addr),
                    daemon=True,
                )
                thread.start()
        except KeyboardInterrupt:
            print("\n[SHUTDOWN] Server is shutting down.")


if __name__ == "__main__":
    start_server()
