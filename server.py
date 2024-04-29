#没啥可说的了，简直一模一样
from server_socket import ServerSocket
from thread import Thread
class server:
    def __init__(self):
        self.socket=ServerSocket()
        self.thread=Thread(self.socket)
        self.thread.start_thread(
            attept_thread=self.socket.accept,#多了一个，但我没力气了，懂的都懂
            send_thread=self.socket.send,
            receive_thread=self.socket.receive,
        )
        if not self.thread.condition:
            self.socket.stop()
