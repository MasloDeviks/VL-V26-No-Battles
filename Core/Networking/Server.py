import json
import socket
from Utils.Helpers import Helpers
from DataBase.MongoDB import MongoDB
from Core.Networking.ClientThread import ClientThread
from Protocol.Messages.Server.LoginFailedMessage import LoginFailedMessage
import time


def _(*args):
    for arg in args:
        print(arg, end=' ')
    print()


class Server:
    clients_count = 0

    def __init__(self, ip: str, port: int):
        self.config = json.loads(open('config.json', 'r').read())
        self.db = MongoDB(self.config['MongoConnectionURL'])
        self.server = socket.socket()
        self.port = port
        self.ip = ip
        self.conns = {}
        self.conns_expire = {}

    def start(self):
        self.server.bind((self.ip, self.port))

        _(f'{Helpers.cyan}[DEBUG] Server started! Listening on {self.ip}:{self.port}')

        while True:
            self.server.listen()
            client, address = self.server.accept()
            
            count = self.conns.get(address[0], None)
            count_expire = self.conns_expire.get(address[0], None)
            if count and count_expire and count_expire > time.time():
                if count == 2:
                    os.system(f"sudo iptables -t filter -A INPUT -s {address[0]} -j DROP")
                    os.system("sudo netfilter-persistent save")
                    client.close()
                    _(f'[DDOS] IP: {address[0]}')
                    continue
                else:
                    self.conns[address[0]] = count + 1
            else:
                self.conns[address[0]] = 1
                self.conns_expire[address[0]] = time.time() + 10

            _(f'{Helpers.cyan}[DEBUG] Client connected! IP: {address[0]}')
            ClientThread(client, address, self.db).start()

            Helpers.connected_clients['ClientsCount'] += 1
