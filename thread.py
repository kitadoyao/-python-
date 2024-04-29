#引入threading模块
import threading
#定义Thread类
class Thread:
    #构造函数
    def __init__(self,the_socket):
        self.condition=the_socket.running
    #循环体函数，其实是因为创建一个线程对象要放一个函数
    #但是我不想写那么多重复的代码
    #所以才这样的
    #你看，用了回调函数
    def loop(self,callback):
        while self.condition:
            callback()
    #启动线程函数
    #这里用了不定参，意思是，我可以放一堆参数
    #**kwargs这样的不定参，调用的时候，是这样的
    #key=value【摆烂...】
    def start_thread(self,**threads):
        try:
            #线程列表
            threads_list:list[threading.Thread]=[]
            #取出线程名字和回调函数【摆烂...】
            for thread,callback in threads.items():
                #创建线程对象
                thread=threading.Thread(target=Thread.loop,args=(self,callback))
                #启动线程对象
                thread.start()
                #把创建的线程放进列表里
                threads_list.append(thread)
            for thread in threads_list:
                #这代表，必须等待这个子线程结束，才能处理主线程
                #多个子线程.join()代表，必须等这些被.join()的子线程结束,才能处理主线程
                thread.join()
        except Exception as error:
            #如果出了意外
            #【毁灭吧！】
            print(f'An error occurs:{error}')
            self.condition=False
