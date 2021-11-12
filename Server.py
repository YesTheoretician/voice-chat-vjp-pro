import socket
import threading
import time

PASSWORD = 'a'

class Server:
    def __init__(self):
        self.ip = '192.168.100.7'
        # self.ip = socket.gethostbyname(socket.gethostname())
        while 1:
            try:
                self.port = 42069
                self.text_port = 42070

                self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                self.ts = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

                self.s.bind((self.ip, self.port))
                self.ts.bind((self.ip, self.text_port))

                break
            except:
                print("Couldn't bind to that port")

        self.connections = []
        self.text_connections = []

        # threading.Thread(target=self.update_client).start()

        self.accept_connections()

    def accept_connections(self):
        self.s.listen(100)
        self.ts.listen(100)

        print('Running on IP: ' + self.ip)
        print('Running on port: ' + str(self.port), str(self.text_port))

        threading.Thread(target=self.update_client).start()

        while True:
            c, addr = self.s.accept()
            text_c, text_addr = self.ts.accept()
            if self.authenticate(c):
                print('New connection created!')
                self.connections.append(c)
                self.text_connections.append(text_c)
                threading.Thread(target=self.handle_client, args=(c, addr,)).start()
                threading.Thread(target=self.handle_text_client, args=(text_c, text_addr,)).start()

    # TODO: auto update self.connections when a client disconnects

    def authenticate(self, sock):
        try:
            data = sock.recv(1024)
            data = data.decode()
            # print('Received authentication password:', data)
            if data == PASSWORD:
                sock.sendall('200'.encode())
                return True
            else:
                sock.sendall('-1'.encode())
                return False
        except:
            return False

    def is_socket_closed(self, sock):
        try:
            # this will try to read bytes without blocking and also without removing them from buffer (peek only)
            data = sock.recv(16, socket.MSG_DONTWAIT | socket.MSG_PEEK)
            if len(data) == 0:
                return True
        except BlockingIOError:
            return False  # socket is open and reading from it would block
        except ConnectionResetError:
            return True  # socket was closed for some other reason
        except Exception as e:
            # logger.exception("unexpected exception when checking if a socket is closed")
            return False
        return False

    def update_client(self):
        while True:
            self.connections = [x for x in self.connections if not self.is_socket_closed(x)]
            self.text_connections = [x for x in self.text_connections if not self.is_socket_closed(x)]
            # print('Broadcasting to', len(self.connections), 'devices')
            time.sleep(40)

    def broadcast(self, sock, data):
        for client in self.connections:
            if client != self.s and client != sock:
                try:
                    client.send(data)
                except:
                    pass

    def text_broadcast(self, sock, data):
        for client in self.text_connections:
            if client != self.s and client != sock:
                try:
                    client.send(data)
                except:
                    pass

    def handle_client(self, c, addr):
        while 1:
            try:
                data = c.recv(1024)
                self.broadcast(c, data)

            except socket.error:
                c.close()
                return

    def handle_text_client(self, c, addr):
        while 1:
            try:
                data = c.recv(1024)
                self.text_broadcast(c, data)

            except socket.error:
                c.close()
                return


server = Server()