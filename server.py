from server_socket import ServerSocket
from thread_manager import ThreadManager
class Server:
    def __init__(self):
        self.socket=ServerSocket()
        self.thread=ThreadManager(self.socket)
        self.thread.start_threads(self.socket.accept,self.socket.receive)
