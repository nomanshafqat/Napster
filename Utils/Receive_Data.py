

def receive_data(sock):
    data = sock.recv(32).strip()
    length = int(str(data.decode('utf-8')))
    # read the data
    temp = sock.recv(1024).strip()
    data=temp
    while (temp):
        print( "Receiving...")
        temp= sock.recv(2048)
        data+=temp
    return data