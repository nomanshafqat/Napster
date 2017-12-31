
import socket

def send_data(data,HOST,PORT):

    data = data.encode('utf-8')
    length = str(len(data)).encode('utf-8')
    while len(length) < 32:
        length = "0".encode("utf-8") + length

    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect((HOST, PORT))

    sock.sendall(length)
    sock.sendall(data)
    return sock

def send_data_sock(data,sock):

    data = data.encode('utf-8')
    length = str(len(data)).encode('utf-8')
    while len(length) < 32:
        length = "0".encode("utf-8") + length

    sock.sendall(length)
    sock.sendall(data)
    return sock

def send_binary_file(data,filename,sock):

    length = str(len(data)).encode('utf-8')
    while len(length) < 32:
        length = "0".encode("utf-8") + length

    sock.sendall(length)


    sock.sendall(data)
    return sock