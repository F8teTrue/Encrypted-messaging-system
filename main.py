import socket
import threading
import rsa

def receive_messages(sock, sender):
    """
    Listens continiously for data on the socket, then decodes it and prints it.
    """
    while True:
        try:
            data = rsa.decrypt(sock.recv(1024), private_key).decode('UTF-8') # This is listening for incomming data on the socket and decrypts it.
            if not data:
                print(f'Connection with {sender} closed.')
                break
            print(f'Received from {sender}: {data}')
        
        # When partner exits you get a decryption error and instead the following is printed.
        except rsa.DecryptionError:
            print('Partner has disconnected. Press enter to close.')
            break

        # If an error occurs the socket is closed.
        except OSError as e: 
            if e.errno == 9:
                print("Connection closed.")
                break
            else:
                raise
    sock.close()

def send_messages(sock):
    """
    Takes user input and sends it to the connected socket.
    """
    while True:
        try:
            message = input("-> ")
            if message.lower() == "exit":
                print("Closing connection.")
                sock.close()
                break
            sock.send(rsa.encrypt(message.encode('utf-8'), public_partner)) # This encrypts the message using partners public key and sends it to the connected socket.

            # Same again. If an error occurs the socket is closed.
        except OSError as e:
            if e.errno == 9:
                print("Connection closed.")
                break
            else:
                raise

public_key, private_key = rsa.newkeys(1024) # Generates key pair for encryption and decryption
public_partner = None

hosting = input("Do you want to host (1) or connect (2): ")


if hosting == "1":
# The host creates a socket and binds it to an IP (any in this case) and a port.
# It then listens for incomming connections and then wait for a client to connect and returns a new socket

    host = "0.0.0.0"
    port = 4000

    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

    s.bind((host, port))
    s.listen()
    print("Server started")
    print('"exit" to close.')


    c, _ = s.accept()
    print("Client connected")

    # Sends own public key to partner and revieves partners public key
    c.send(public_key.save_pkcs1("PEM"))
    public_partner = rsa.PublicKey.load_pkcs1(c.recv(1024))

# This starts 2 threads, 1 for recieving messages and one for sending messages.
    receive_thread = threading.Thread(target=receive_messages, args=(c, "client"))
    send_thread = threading.Thread(target=send_messages, args=(c,))

    receive_thread.start()
    send_thread.start()

# Waits for both threads to finish and closes the sockets after.
    receive_thread.join()
    send_thread.join()
    c.close()
    s.close()

elif hosting == "2":
# The client creates a socket and connects to the host using the hosts IP and the chosen port.

    server = "10.58.176.2"
    port = 4000

    c = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    c.connect((server, port))
    
    # Again sends own public key to partner and revieves partners public key
    public_partner = rsa.PublicKey.load_pkcs1(c.recv(1024))
    c.send(public_key.save_pkcs1("PEM"))

    print("Connected to host.")
    print('"exit" to close.')

# Same as the host with starting the 2 threads for recieving and sending messages.
    receive_thread = threading.Thread(target=receive_messages, args=(c, "host"))
    send_thread = threading.Thread(target=send_messages, args=(c,))

    receive_thread.start()
    send_thread.start()

else:
    print("Not a valid choice. Try again.")
    exit()


