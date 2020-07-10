import socket

class Networking_server:
    def __init__(self):
        self.connection = None
        self.client_address = None
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_address = ('', 10000)
        self.sock.bind(self.server_address)
        self.sock.listen()
        self.flag = False
        while not self.flag:
            self.connection, self.client_address = self.sock.accept()
            if self.connection:
                self.flag = True

    def send(self, message):
        message = str(message)
        message = message.encode()
        self.connection.sendall(message)

    def listening(self):
        txt = ""
        while txt != 'exit':
            try:
                data = self.connection.recv(4096)
                data = data.decode('utf-8')
                txt = data
                if txt == "exit":
                    self.broken = True
                data = eval(data)
                return data
            except:
                pass

    def close_it(self):
        self.sock.close()
