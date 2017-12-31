import json
import os
import socketserver
import threading
from Utils.Send_Data import send_data, send_data_sock
from Utils.Receive_Data import receive_data
import string
import random
from difflib import SequenceMatcher

dic = {}
''' "id" : ["filename","ip","port"]'''


def generate_unique_file_id():
    randomnum = ''.join([random.choice(string.ascii_letters + string.digits) for n in range(0, 64)])
    return randomnum


def similar(a, b):
    return SequenceMatcher(None, a, b).ratio()


class ThreadedTCPRequestHandler(socketserver.BaseRequestHandler):
    def handle(self):
        global dic
        # receive the length
        self.data = self.request.recv(32).strip()
        length = int(str(self.data.decode('utf-8')))
        print("incoming packet length", length)

        # read the json  data
        self.data = self.request.recv(length).strip()
        jsondata = json.loads(str(self.data.decode('utf-8')))

        if jsondata["command"] == "seed":
            print("Seed request", self.client_address)
            id = generate_unique_file_id()
            send_data_sock(id, self.request)
            print("Id sent...")
            dic[id] = [jsondata["filename"], jsondata["ip"], jsondata["port"]]
            print(dic)
        elif jsondata["command"] == "get":
            print("get request", self.client_address)
            print(jsondata)
            filename_ip_port = dic[jsondata["fileid"]]

            data = {"command": "getserreply", "filename": filename_ip_port[0], "ip": filename_ip_port[1],
                    "port": filename_ip_port[2]}
            data = json.dumps(data)

            print(str(filename_ip_port))
            send_data_sock(data, self.request)

        elif jsondata["command"] == "search":
            print("search request", self.client_address)
            q = jsondata["q"]

            searchresults = [("key","filename")]

            if len(dic.keys()) > 0:
                for key in dic.keys():
                    if similar(dic[key][0], q) > 0.9:
                        searchresults.append(( key,dic[key][0]))
                    elif q in dic[key][0]:
                        searchresults.append(( key,dic[key][0]))

            searchresults = str(searchresults)

            send_data_sock(searchresults, self.request)


            return
            # TODO search in the dic for filename and return the filename and file id from dic[file_id]\


class ThreadedTCPServer(socketserver.ThreadingMixIn, socketserver.TCPServer):
    pass


def check_clients():
    # TODO make a thread in main to ping every client after 10mins
    global dic
    if len(dic.keys()) > 0:
        print(dic)


if __name__ == "__main__":

    servername = "server"
    if not os.path.exists(servername):
        os.mkdir(servername)
        os.mkdir(servername + "/temp")

    HOST, PORT = "localhost", 9999
    server = ThreadedTCPServer((HOST, PORT), ThreadedTCPRequestHandler)
    ip, port = server.server_address

    # Start a thread with the server -- that thread will then start one
    # more thread for each request
    server_thread = threading.Thread(target=server.serve_forever)
    # Exit the server thread when the main thread terminates
    server_thread.daemon = True
    server_thread.start()

    server.serve_forever()
