import socket
import threading
import sys

Port = 5050
Host = socket.gethostbyname(socket.gethostname())

client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)