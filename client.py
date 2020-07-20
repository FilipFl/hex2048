import socket


class Networking_client:

    def __init__(self, address):
        self.connection = None
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_address = (address, 10000)
        self.sock.connect(self.server_address)

    def send(self, message):
        message = str(message)
        message = message.encode()
        self.sock.sendall(message)

    def listening(self):
        txt = ""
        while txt != 'exit':
            try:
                data = self.sock.recv(4096)
                data = data.decode('utf-8')
                txt = data
                if txt == "exit":
                    self.broken = True
                data = eval(data)
                return data
            except:
                pass
        return False
