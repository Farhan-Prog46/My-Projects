import socket
import threading

Port = 5050
Host = socket.gethostbyname(socket.gethostname())

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind((Host, Port))
server.listen()

Username = []
Password = []