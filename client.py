#加把劲！还有两个文件！
#好短的代码，我喜欢，不用写太多注释
#去看client_socket.py，不要在这个文件问我client_socket.py的内容
from client_socket import ClientSocket
#同上，去看thread.py文件
from thread import Thread
class client:
    def __init__(self):
        self.socket=ClientSocket()#我创建啦！
        self.thread=Thread(self.socket)#我也创建啦！
        self.socket.start()#啦啦啦啦啦~
        self.thread.start_thread(
            send_thread=self.socket.send,#懂我说的意思了吧？
            receive_thread=self.socket.receive,
            heartbeat_thread=self.socket.heartbeat
        )
        if not self.thread.condition:
            self.socket.stop()#如果你死了，那么我也死了
