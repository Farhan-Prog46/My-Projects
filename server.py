import socket
import threading

from datetime import datetime
from Database import (
    init_db,
    create_user,
    authenticate_user,
    store_message,
    ban_user,
    unban_user
)

HOST = socket.gethostbyname(socket.gethostname())
PORT = 5050
MAX_CONNECTIONS = 10

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind((HOST, PORT))
server.listen(MAX_CONNECTIONS)

# stores (conn, username)
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
                pass


def kick_user(target_username: str):
    """Temporary kick: disconnect a user WITHOUT banning them."""
    kicked = None
    with clients_lock:
        for conn, username in list(clients):
            if username == target_username:
                # remove while holding lock to keep list consistent
                try:
                    clients.remove((conn, username))
                except ValueError:
                    pass
                kicked = (conn, username)
                break

    # perform network IO and broadcasting outside the lock to avoid deadlocks
    if not kicked:
        return

    conn, username = kicked
    try:
        conn.sendall(b"[SYSTEM] You have been kicked from the chat.\n")
    except Exception:
        pass
    try:
        conn.close()
    except Exception:
        pass

    broadcast(f"[SYSTEM] {username} was kicked from the chat.\n")
    print(f"[ADMIN] Kicked {username}")


def handle_client(conn: socket.socket, addr) -> None:
    print(f"[NEW CONNECTION] {addr} connected.")
    username = None
    authenticated = False

    try:
        # -------- LOGIN / REGISTER LOOP --------
        while not authenticated:
            data = conn.recv(1024)
            if not data:
                conn.close()
                return

            message = data.decode("utf-8").strip()
            parts = message.split("|")
            command = parts[0]

            # REGISTER
            if command == "REGISTER" and len(parts) == 4:
                email = parts[1]
                username_try = parts[2]
                password = parts[3]

                if create_user(email, username_try, password):
                    conn.sendall(b"REGISTER_OK|Account created successfully. Please log in.\n")
                else:
                    conn.sendall(b"REGISTER_FAIL|Username or email already exists.\n")

            # LOGIN
            elif command == "LOGIN" and len(parts) == 3:
                username_try = parts[1]
                password = parts[2]

                result = authenticate_user(username_try, password)

                if result == "Banned":
                    conn.sendall(b"LOGIN_FAIL|You are banned from this server.\n")
                    return

                if result is True:
                    username = username_try
                    authenticated = True
                    conn.sendall(b"LOGIN_OK|Login successful.\n")
                else:
                    conn.sendall(b"LOGIN_FAIL|Invalid credentials.\n")

            else:
                conn.sendall(b"ERROR|Invalid command.\n")

        # -------- ADD CLIENT TO LIST --------
        with clients_lock:
            clients.append((conn, username))

        broadcast(f"[SYSTEM] {username} joined the chat.\n")
        print(f"[SYSTEM] {username} joined the chat.")

        # -------- CHAT LOOP --------
        while True:
            data = conn.recv(1024)
            if not data:
                break

            message = data.decode("utf-8").strip()

            # ----- ADMIN COMMANDS -----
            if username == "admin":

                if message.startswith("KICK|"):
                    target = message.split("|", 1)[1]
                    kick_user(target)
                    continue

                if message.startswith("BAN|"):
                    target = message.split("|", 1)[1]
                    if ban_user(target):
                        broadcast(f"[SYSTEM] {target} has been banned.\n")
                    else:
                        conn.sendall(b"ERROR|User does not exist.\n")
                    continue

                if message.startswith("UNBAN|"):
                    target = message.split("|", 1)[1]
                    if unban_user(target):
                        broadcast(f"[SYSTEM] {target} has been unbanned.\n")
                    else:
                        conn.sendall(b"ERROR|User does not exist.\n")
                    continue

            # ----- NORMAL MESSAGE -----
            if message.startswith("MSG|"):
                text = message[4:].strip()
                if text:
                    store_message(username, text)
                    timestamp = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
                    broadcast(f"[{timestamp}] {username}: {text}\n")
                continue

    except Exception as e:
        print(f"[ERROR] {addr}: {e}")

    finally:
        with clients_lock:
            clients[:] = [(c, u) for (c, u) in clients if c is not conn]

        conn.close()

        if username:
            broadcast(f"[SYSTEM] {username} left the chat.\n")
            print(f"[SYSTEM] {username} left the chat.")

        print(f"[CONNECTION CLOSED] {addr}")


def start_server():
    init_db()
    print(f"[SERVER STARTED] Listening on {HOST}:{PORT}")

    try:
        while True:
            conn, addr = server.accept()
            threading.Thread(target=handle_client, args=(conn, addr), daemon=True).start()

    except KeyboardInterrupt:
        print("\n[SERVER SHUTDOWN] Graceful exit.")


if __name__ == "__main__":
    start_server()
