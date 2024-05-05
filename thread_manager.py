import threading
class ThreadManager:
    def __init__(self,the_socket):
        self.socket=the_socket
    def loop(self,callback):
        while True:
            if not self.socket.running:
                break
            callback()
    def start_threads(self,*callbacks):
        try:
            for callback in callbacks:
                threading.Thread(target=self.loop,args=(callback,)).start()
        except Exception as error:
            print(f'An error occurs:{error}')
    def stop_threads(self):
        self.socket.running=False
