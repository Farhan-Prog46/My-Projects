# TCP Chatroom (Python + Sockets + SQLAlchemy + Docker)

## How to run using Docker
1. Build the image:
   docker build -t chatserver .

2. Run the container:
   docker run -p 5050:5050 chatserver

## How to run client (local)
python3 client.py
