import socket
import threading
import rsa
from Crypto.Cipher import AES
from secrets import token_bytes
import pickle

def encrypt_aes(msg, key):
    """
    Kryptheierer meldingen med bruk av AES.
    """
    cipher = AES.new(key, AES.MODE_EAX)
    nonce = cipher.nonce
    cipherText, tag = cipher.encrypt_and_digest(msg.encode('utf-8'))
    return nonce, cipherText, tag

def decrypt_aes(nonce,cipherText, tag, key):
    """
    Dekrypterer meldingen med bruk av AES.
    """
    cipher = AES.new(key, AES.MODE_EAX, nonce=nonce)
    plainText = cipher.decrypt(cipherText)
    try:
        cipher.verify(tag)
        return plainText.decode('utf-8')
    except:
        return False

def receive_messages(sock, sender):
    """
    Listens continiously for data on the socket, then decodes it and prints it.
    """
    while True:
        try:
            data = sock.recv(2048)
            if not data:
                print(f'Connection with {sender} closed. \n "exit" to close.')
                break
            encrypted_aes_key, nonce, cipherText, tag = pickle.loads(data)
            aes_key = rsa.decrypt(encrypted_aes_key, private_key)
            message = decrypt_aes(nonce, cipherText, tag, aes_key)

            if not message:
                print(f'Connection with {sender} closed.')
                break
            print(f'Received from {sender}: {message}')
        
        except rsa.DecryptionError:
            print("DECRYPTION ERROR! Press ctrl + c to exit.")
            break
        except OSError as e:
            if e.errno == 9:
                break
            else:
                raise
        except KeyboardInterrupt:
            print('Connection closed.')
            break
    sock.close()

def send_messages(sock):
    """
    Takes user input and sends it to the connected socket.
    """
    while True:
        try:
            message = input("-> ")
            if message.lower() == "exit":
                print('Connection closed.')
                sock.close()
                break

            if not message.strip():
                print('Message cannot be empty.')
                continue

            # Creates a new AES key for each message and encrypts the message with it.
            aes_key = token_bytes(24)
            nonce, cipherText, tag = encrypt_aes(message, aes_key)
            encrypted_aes_key = rsa.encrypt(aes_key, public_partner)

            # Serialize the tuple to a byte stream using pickle, then sends it over the socket.
            data = pickle.dumps((encrypted_aes_key, nonce, cipherText, tag))
            sock.send(data)

        except OSError as e:
            if e.errno == 9:
                print('An error has occured.')
                print('Connection closed. \n "exit" to close.')
                break
            else:
                raise



public_key, private_key = rsa.newkeys(1024) # Generates a RSA key pair for encryption and decryption of the AES key.
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
    print("Pasting messages might crash the program. Limit for message is terminal limit - 1 character.")


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

    server = "127.0.0.1"
    port = 4000

    c = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    c.connect((server, port))
    
    # Again sends own public key to partner and revieves partners public key
    public_partner = rsa.PublicKey.load_pkcs1(c.recv(1024))
    c.send(public_key.save_pkcs1("PEM"))

    print("Connected to host.")
    print('"exit" to close.')
    print("ctrl + v might crash the program. Limit for message is terminal limit - 1 character.")

# Same as the host with starting the 2 threads for recieving and sending messages.
    receive_thread = threading.Thread(target=receive_messages, args=(c, "host"))
    send_thread = threading.Thread(target=send_messages, args=(c,))

    receive_thread.start()
    send_thread.start()

else:
    print("Not a valid choice. Try again.")
    exit()


