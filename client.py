import socket
import threading
import sys

HOST = "localhost"
PORT = 5050

def receive_messages(client_socket: socket.socket) -> None:
    """Continuously receive and print messages from the server."""
    while True:
        try:
            data = client_socket.recv(1024)
            if not data:
                print("\n[INFO] Server closed the connection.")
                break

            text = data.decode("utf-8")
            print("\n" + text, end="")
            print("> ", end="", flush=True)
        except Exception:
            break

    try:
        client_socket.close()
    except OSError:
        pass

    sys.exit(0)

def main() -> None:
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        client_socket.connect((HOST, PORT))
    except OSError:
        print("[ERROR] Could not connect to server.")
        return

    print(f"[CONNECTED] Connected to chat server at {HOST}:{PORT}")

    # -------- LOGIN / REGISTER LOOP ----------
    while True:
        try:
            print("\n1. Log in")
            print("2. Create new account")
            print("Press Ctrl+C to exit.")
            choice = input("Choose an option (1 or 2): ").strip()
        except KeyboardInterrupt:
            print("\n[INFO] Exiting client.")
            client_socket.close()
            sys.exit(0)

        if choice == "1":
            try:
                username = input("Username: ").strip()
                password = input("Password: ").strip()
            except KeyboardInterrupt:
                print("\n[INFO] Exiting client.")
                client_socket.close()
                sys.exit(0)

            message = f"LOGIN|{username}|{password}"
            client_socket.sendall(message.encode("utf-8"))
            response = client_socket.recv(1024).decode("utf-8")
            print(response, end="")
            if response.startswith("LOGIN_OK"):
                break

        elif choice == "2":
            try:
                email = input("Email: ").strip()
                username = input("Choose a username: ").strip()
                password = input("Choose a password: ").strip()
            except KeyboardInterrupt:
                print("\n[INFO] Exiting client.")
                client_socket.close()
                sys.exit(0)

            message = f"REGISTER|{email}|{username}|{password}"
            client_socket.sendall(message.encode("utf-8"))
            response = client_socket.recv(1024).decode("utf-8")
            print(response, end="")

        else:
            print("[INFO] Invalid option. Please enter 1 or 2.")

    print("\nYou are now logged in.")
    print("Type messages and press Enter to send.")
    print("Type /quit or press Ctrl+C to leave.\n")

    # -------- START RECEIVER THREAD ----------
    receiver_thread = threading.Thread(
        target=receive_messages,
        args=(client_socket,),
        daemon=True,
    )
    receiver_thread.start()

    # -------- SEND LOOP ----------
    try:
        while True:
            text = input("> ").strip()
            if not text:
                continue

            if text.lower() == "/quit":
                print("[INFO] Disconnecting.")
                try:
                    client_socket.close()
                except OSError:
                    pass
                sys.exit(0)

            client_socket.sendall(f"MSG|{text}".encode("utf-8"))

    except KeyboardInterrupt:
        print("\n[INFO] Disconnecting.")
        try:
            client_socket.close()
        except OSError:
            pass
        sys.exit(0)

if __name__ == "__main__":
    main()
