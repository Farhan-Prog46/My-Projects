import socket
import threading
import sys

HOST = socket.gethostbyname(socket.gethostname())
PORT = 5050


def receive_messages(client_socket):
    """Receives and prints messages from server."""
    while True:
        try:
            data = client_socket.recv(1024)
            if not data:
                print("\n[INFO] Server closed connection.")
                break

            print("\n" + data.decode(), end="")
            print("> ", end="", flush=True)

        except:
            break

    try:
        client_socket.close()
    except:
        pass

    sys.exit(0)


def main():
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        client.connect((HOST, PORT))
    except:
        print("[ERROR] Could not connect.")
        return

    print("[CONNECTED]")

    # ---------------- LOGIN / REGISTER ----------------
    while True:
        try:
            print("\n1. Login")
            print("2. Register")
            print("Press Ctrl+C to exit.")
            choice = input("Choose an option (1 or 2): ").strip()

        except KeyboardInterrupt:
            print("\n[INFO] Exiting client...")
            client.close()
            sys.exit(0)

        if choice == "1":
            try:
                user = input("Username: ").strip()
                pwd = input("Password: ").strip()
            except KeyboardInterrupt:
                print("\n[INFO] Exiting client...")
                client.close()
                sys.exit(0)

            client.sendall(f"LOGIN|{user}|{pwd}".encode())
            response = client.recv(1024).decode()
            print(response)

            if response.startswith("LOGIN_OK"):
                break

        elif choice == "2":
            try:
                email = input("Email: ").strip()
                user = input("Username: ").strip()
                pwd = input("Password: ").strip()
            except KeyboardInterrupt:
                print("\n[INFO] Exiting client...")
                client.close()
                sys.exit(0)

            client.sendall(f"REGISTER|{email}|{user}|{pwd}".encode())
            print(client.recv(1024).decode())

        else:
            print("[INFO] Invalid choice.")

    # ---------------- RECEIVER THREAD ----------------
    threading.Thread(target=receive_messages, args=(client,), daemon=True).start()

    print("\nCommands:")
    print("/quit")
    print("/kick <user>")
    print("/ban <user>")
    print("/unban <user>\n")

    # ---------------- MAIN SEND LOOP ----------------
    while True:
        try:
            text = input("> ").strip()

            if not text:
                continue

            if text.lower() == "/quit":
                client.close()
                sys.exit(0)

            if text.startswith("/kick "):
                client.sendall(f"KICK|{text.split(' ', 1)[1]}".encode())
                continue

            if text.startswith("/ban "):
                client.sendall(f"BAN|{text.split(' ', 1)[1]}".encode())
                continue

            if text.startswith("/unban "):
                client.sendall(f"UNBAN|{text.split(' ', 1)[1]}".encode())
                continue

            client.sendall(f"MSG|{text}".encode())

        except KeyboardInterrupt:
            print("\n[INFO] Closing connection...")
            client.close()
            sys.exit(0)


if __name__ == "__main__":
    main()
