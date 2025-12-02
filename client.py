import socket
import threading
import sys

HOST = socket.gethostbyname(socket.gethostname())
PORT = 5050


def receive_messages(client_socket: socket.socket) -> None:
    """Continuously receive and print messages from the server."""
    while True:
        try:
            data = client_socket.recv(1024)
            if not data:
                print("\n[INFO] Disconnected from server.")
                break

            text = data.decode("utf-8")
            # Print the message, then re-print the prompt
            print("\n" + text, end="")
            print("> ", end="", flush=True)
        except Exception:
            break

    try:
        client_socket.close()
    except OSError:
        pass

    print("[INFO] Connection closed.")
    sys.exit(0)


def main() -> None:
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        client_socket.connect((HOST, PORT))
    except OSError:
        print("[ERROR] Could not connect to server.")
        return

    print(f"[CONNECTED] Connected to chat server at {HOST}:{PORT}")

    # --------- LOGIN / REGISTER LOOP ----------
    while True:
        print("\n1. Log in")
        print("2. Create new account")
        choice = input("Choose an option (1 or 2): ").strip()

        if choice == "1":
            username = input("Username: ").strip()
            password = input("Password: ").strip()
            message = f"LOGIN|{username}|{password}"
            client_socket.sendall(message.encode("utf-8"))
            response = client_socket.recv(1024).decode("utf-8")
            print(response, end="")

            if response.startswith("LOGIN_OK"):
                break

        elif choice == "2":
            username = input("Choose a username: ").strip()
            password = input("Choose a password: ").strip()
            message = f"REGISTER|{username}|{password}"
            client_socket.sendall(message.encode("utf-8"))
            response = client_socket.recv(1024).decode("utf-8")
            print(response, end="")
            # After REGISTER_OK, user still needs to log in

        else:
            print("[INFO] Invalid option. Please enter 1 or 2.")

    print("\nYou can now start chatting.")
    print("Type messages and press Enter to send.")
    print("Type /quit or press Ctrl+C to leave.\n")

    # --------- START RECEIVER THREAD ----------
    receiver_thread = threading.Thread(
        target=receive_messages,
        args=(client_socket,),
        daemon=True,
    )
    receiver_thread.start()

    # --------- SEND LOOP ----------
    try:
        while True:
            text = input("> ").strip()
            if not text:
                continue

            if text.lower() == "/quit":
                client_socket.sendall("QUIT".encode("utf-8"))
                break

            client_socket.sendall(f"MSG|{text}".encode("utf-8"))

    except KeyboardInterrupt:
        print("\n[INFO] Stopped")
        try:
            client_socket.sendall("QUIT".encode("utf-8"))
        except OSError:
            pass
    finally:
        try:
            client_socket.close()
        except OSError:
            pass
        sys.exit(0)


if __name__ == "__main__":
    main()
