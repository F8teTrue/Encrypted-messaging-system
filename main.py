import socket
import sys
import threading
import rsa

def recieve_messages(sock):
    while True:
        data, addr = sock.recvfrom(1024)
        data = data.decode("utf-8")
        print(f'Recieved from {addr}: {data}')

def server():
    host = "127.0.0.1"
    port = 4000

    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.bind((host, port))

    print("Server started")

    recieve_thread = threading.Thread(target = recieve_messages, args = (s,))
    recieve_thread.start()

    while True:
        message = input("-> ")
        s.sendto(message.encode('utf-8'), ('127.0.0.1', 4005))

def client():
    host = "127.0.0.1"
    port = 4005

    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.bind((host, port))

    recieve_thread = threading.Thread(target = recieve_messages, args = (s,))
    recieve_thread.start()

    while True:
        message = input("-> ")
        s.sendto(message.encode('utf-8'), ('127.0.0.1', 4000))

if __name__ == '__main__':
    if len(sys.argv) != 2:
        print("Usage: python Main.py host|client")
        sys.exit(1)

    if sys.argv[1] == 'host':
        server()
    elif sys.argv[1] == 'client':
        client()
    else:
        print("Invalid argument. Use 'host' or 'client'.")


