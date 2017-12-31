import json
import os
import shutil
import socket
import socketserver
import threading
import time
from threading import Thread
from Utils.Send_Data import send_data, send_data_sock, send_binary_file
from Utils.Send_Data import send_data
from Utils.Receive_Data import receive_data


class ThreadedTCPClientRequestHandler(socketserver.BaseRequestHandler):
    def handle(self):

        # receive the length
        self.data = self.request.recv(32).strip()
        length = int(str(self.data.decode('utf-8')))
        print("incoming packet length", length)

        # read the data
        self.data = self.request.recv(length).strip()
        jsondata = json.loads(str(self.data.decode('utf-8')))

        if jsondata["command"] == "get":
            print("client receive the file request")
            fileid = jsondata["fileid"]
            global dic
            print(dic)
            path = os.path.join(dic[fileid][1], dic[fileid][0])
            f = open(path, 'rb')
            filecontents = f.read()
            send_binary_file(filecontents, "sds", self.request)
            print("File Sent")

        if jsondata["command"] == "ping":
            # TODO ACK to ping
            return


class ThreadedTCPServer(socketserver.ThreadingMixIn, socketserver.TCPServer):
    pass


# dic["file_id"] = [filename,path]
dic = {}
hostingat = ("localhost", 9435)  # client hosting at


def get_server_address_port():
    return "localhost", 9999


def get_unique_id_from_server(filename):
    global hostingat
    data = {"command": "seed", "filename": filename, "ip": hostingat[0], "port": hostingat[1]}
    data = json.dumps(data)
    HOST, PORT = get_server_address_port()

    sock = send_data(data, HOST, PORT)
    id = receive_data(sock).decode('utf-8')

    return id


def seedfile(filename, path):
    global dic
    print("Sending Seeding request for " + filename + " in " + path)
    id = get_unique_id_from_server(filename)
    dic[id] = [filename, path]
    print(dic)
    return


def convert_to_json(data):
    return json.loads(str(data.decode('utf-8')))


def getfile(file_id):
    data = {"command": "get", "fileid": file_id}
    data = json.dumps(data)
    HOST, PORT = get_server_address_port()

    sock = send_data(data, HOST, PORT)
    clientinfo = receive_data(sock).decode('utf-8')

    jsondata = json.loads(clientinfo)

    sock = send_data(data, jsondata["ip"], int(jsondata["port"]))
    data = receive_data(sock)
    f = open(jsondata["filename"], "wb")
    f.write(data)
    f.close()
    print("file received")


def search(q):
    data = {"command": "search", "q": q}
    data = json.dumps(data)
    HOST, PORT = get_server_address_port()

    sock = send_data(data, HOST, PORT)
    clientinfo = receive_data(sock).decode('utf-8')
    clientinfo=clientinfo.split(",")
    print(clientinfo)
    for i in range(0,len(clientinfo),2):

        print(clientinfo[i][3:-1],clientinfo[i+1][2:-2])



    return


def start_request_handler():
    HOST, PORT = hostingat
    server = ThreadedTCPServer((HOST, PORT), ThreadedTCPClientRequestHandler)
    ip, port = server.server_address

    # Start a thread with the server -- that thread will then start one
    # more thread for each request
    server_thread = threading.Thread(target=server.serve_forever)
    # Exit the server thread when the main thread terminates
    server_thread.daemon = True
    server_thread.start()

    server.serve_forever()


if __name__ == "__main__":
    server_thread = threading.Thread(target=start_request_handler)
    server_thread.daemon = True
    server_thread.start()
    '''
    seed  [filename] [path]
    get [file_id]
    search [string]
get sdfsfsfdsf
seed miley_cyrus_wrecking_ball_My2FRPA3Gf8_320kbps.mp3 /Users/nomanshafqat/Downloads
search miley_cyrus_wrecking_ball_My2FRPA3Gf8_320kbps
    '''
    while (True):
        try:

            command = input('>>')
            arg = command.split(" ")

            if arg[0] == "seed":
                seedfile(arg[1], arg[2])
            if arg[0] == "get":
                getfile(arg[1])
            if arg[0] == "search":
                search(arg[1])
        except:
            print("Bad Param")
            print('''seed  [filename] [path]
            get [file_id]
            search [string]''')
            continue
