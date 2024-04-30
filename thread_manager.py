import threading
class ThreadManager:
    def __init__(self,the_socket):
        self.socket=the_socket
    def loop(self,callback):
        while True:
            if not self.socket.running:
                break
            callback()
    def start_thread(self,*callbacks):
        try:
            for callback in callbacks:
                threading.Thread(target=self.loop,args=(self,callback)).start()
        except Exception as error:
            print(f'An error occurs:{error}')
