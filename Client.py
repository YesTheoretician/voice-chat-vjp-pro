import socket
import threading
import pyaudio
from os import system


class Client:
    def __init__(self):
        self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.ts = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        while 1:
            try:
                # self.target_ip = input('Enter IP address of server --> ')
                # self.target_port = int(input('Enter target port of server --> '))

                self.target_ip = '113.178.71.84'
                self.target_port = 42069

                self.target_text_port = 42070

                self.s.connect((self.target_ip, self.target_port))
                self.ts.connect((self.target_ip, self.target_text_port))

                break
            except:
                print("Couldn't connect to server")

        self.authenticate()

        chunk_size = 1024  # 512
        audio_format = pyaudio.paInt16
        channels = 1
        rate = 20000

        # initialise microphone recording
        self.p = pyaudio.PyAudio()
        self.playing_stream = self.p.open(format=audio_format, channels=channels, rate=rate, output=True,
                                          frames_per_buffer=chunk_size)
        self.recording_stream = self.p.open(format=audio_format, channels=channels, rate=rate, input=True,
                                            frames_per_buffer=chunk_size)

        print("Connected to Server")

        # start threads
        receive_thread = threading.Thread(target=self.receive_server_data).start()

        text_thread = threading.Thread(target=self.send_text_data_to_server).start()
        text_recv = threading.Thread(target=self.receive_server_text_data).start()

        self.send_data_to_server()

    def authenticate(self):
        try:
            passphrase = input('Input your passphrase (you can\'t bypass this, don\'t even try): ')
            while passphrase == '':
                passphrase = input('Pls enter a meaningful sequence: ')
            passphrase = passphrase.encode()
            self.s.sendall(passphrase)
            result = self.s.recv(1024).decode()
            if result == '200':
                print('AUTHENTICATION SUCCESSFUL!')
            else:
                print('AUTHENTICATION FAILED')
                system('pause')
                exit(-1)
        except:
            print('Error, please try running again!')
            exit(-1)

    def receive_server_data(self):
        while True:
            try:
                voice_data = self.s.recv(1024)
                self.playing_stream.write(voice_data)
            except:
                pass

    def receive_server_text_data(self):
        while True:
            try:
                text_data = self.ts.recv(1024)
                print(text_data.decode())
            except:
                pass

    def send_data_to_server(self):
        while True:
            try:
                data = self.recording_stream.read(1024)
                self.s.sendall(data)
                # self.s.close()
            except:
                pass

    def send_text_data_to_server(self):
        while True:
            try:
                data = input().encode()
                self.ts.sendall(data)
                # print('Gui thanh cong')
            except:
                pass


client = Client()