from client_socket import ClientSocket
from thread_manager import ThreadManager
class Client:
    def __init__(self):
        self.socket=ClientSocket()
        self.thread=ThreadManager(self.socket)
        self.thread.start_thread(self.socket.send,self.socket.receive,self.socket.heartbeat)
