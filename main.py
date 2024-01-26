import socket
import threading
import rsa

def receive_messages(sock, sender):
    while True:
        try:
            data = sock.recv(1024)
            if not data:
                print(f'Connection with {sender} closed.')
                break
            data = data.decode("utf-8")
            print(f'Received from {sender}: {data}')
        except OSError as e:
            if e.errno == 9:
                print("Connection closed.")
                break
            else:
                raise
    sock.close()

def send_messages(sock):
    while True:
        try:
            message = input("-> ")
            if message.lower() == "exit":
                print("Closing connection.")
                sock.close()
                break
            sock.send(message.encode('utf-8'))
        except OSError as e:
            if e.errno == 9:
                print("Connection closed.")
                break
            else:
                raise


hosting = input("Do you want to host (1) or connect (2): ")

if hosting == "1":
    host = "0.0.0.0"
    port = 4000

    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

    s.bind((host, port))
    s.listen()
    print("Server started")
    print('"exit" to close.')


    c, _ = s.accept()

    receive_thread = threading.Thread(target=receive_messages, args=(c, "client"))
    send_thread = threading.Thread(target=send_messages, args=(c,))

    receive_thread.start()
    send_thread.start()

    receive_thread.join()
    send_thread.join()
    c.close()
    s.close()

elif hosting == "2":
    client = "10.58.176.2"
    port = 4000

    c = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    c.connect((client, port))

    print("Connected to host.")
    print('"exit" to close.')

    receive_thread = threading.Thread(target=receive_messages, args=(c, "host"))
    send_thread = threading.Thread(target=send_messages, args=(c,))

    receive_thread.start()
    send_thread.start()

else:
    print("Not a valid choice. Try again.")
    exit()


