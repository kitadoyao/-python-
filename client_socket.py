#太长了，不想写注释怎么办？
#啊啊啊！怎么办呢？！
#还是写吧...
#引入socket模块
#我想吐槽这个名字，为什么要翻译成套接字
import socket
#引入time模块，处理时间相关的
import time
#终于！终于！
#终于看到我写的东东了！【雾（】
#这个是config.py的东东，不知道的赶紧去看
from config import Config
#这个是message.py的东东，不知道的赶紧去看
from message import Message
#定义ClientSocket类~
#啊吧啊吧，好长啊...
class ClientSocket:
    #一个初始化，不会有人不知道吧
    def __init__(self):
        #欸？为什么这里可以放函数？
        #当然可以放，现在我告诉你了
        self._init_socket()
        #取本机ip地址
        self.id=socket.gethostname()
        #我还活着
        self.running=True
        #服务端没死
        self.server_disconnected=False
    def _init_socket(self):
        #创建一个socket对象
        self.socket=socket.socket(socket.AF_INET,socket.SOCK_STREAM)
        #我连的服务端【雾（】
        self.socket.connect((Config.serverHost,Config.usingPort))
    def start(self):
        #事先给服务端发送个信息
        #我给大伙们翻译翻译
        #“啊！亲爱的服务端酱！请让我这个客户端小妹妹加入你的聊天吧！”
        self.send(Config.MessageType.inquire,Config.Instruction.please,self.id,Config.serverId)
    def stop(self):
        #如果我死了
        self.running=False
        #等于我死了
        self.socket.close()
        #大伙们都能看懂，我就不说了
    def send(self,type,instruction,sender,addressee,content=''):
        MESSAGE=Message.dumps(type,instruction,sender,addressee,content)
        self.socket.sendall(MESSAGE)
        self.handle_send(MESSAGE)
        #懂的都懂
    def receive(self):
        MESSAGE=self.socket.recv(Config.maximumTextLimit).decode()
        self.handle_receive(MESSAGE) if Message.is_message(MESSAGE) else None
    #啊啊啊！！！好长啊！！！我要放弃了！！！写注释好累！！！
    def handle_send(self,message):
        match message['type']:
            case Config.MessageType.inquire:
                match message["instruction"]:
                    #如果我说了一声“bye-bye”，那就是真的bye-bye！
                    case Config.Instruction.bye:
                        self.stop()
    def handle_receive(self,message):
        #这么简单的代码，真的有人看不懂吗？
        if message is not None:
            DICTIONARY=Message.loads(message)
            if type(DICTIONARY)==dict:
                match DICTIONARY['type']:
                    #啊~如果你是送我的
                    case Config.MessageType.transmit:
                        match DICTIONARY['instruction']:
                            #而且是文本~【只有文本啊！！！我没写怎么处理发送文件！！！】
                            case Config.Instruction.text:
                                print(f'A message from {DICTIONARY['sender']}\n')
                                print('Main body:\n')
                                print(f'{DICTIONARY['content']}\n')
                    case Config.MessageType.detection:#活着吗？服务端大哥？
                        match DICTIONARY['instruction']:
                            case Config.Instruction.detect:
                                match DICTIONARY['sender']:
                                    case Config.serverId:
                                        self.server_disconnected=False#没死，那就是活着
                    case Config.MessageType.inquire:
                        match DICTIONARY['instruction']:
                            case Config.Instruction.bye:#你说了bye-bye了是吧？
                                print(f'Addressee {DICTIONARY['sender']} stopped communication')
                    case Config.MessageType.respond:
                        match DICTIONARY['sender']:
                            case Config.serverId:#是服务端大哥啊
                                match DICTIONARY['instruction']:
                                    case Config.Instruction.id:#我的名字吗？id2333，牛逼
                                        print(f'You has been assigned an ID:{DICTIONARY['content']}')
                                        self.sender_id=DICTIONARY['content']
                                    case Config.Instruction.known:#服务端：“朕知道了”
                                        print('Reconnecting to the server succeeded.')
    def heartbeat(self):#死了吗？
        self.send(Config.MessageType.detection,Config.Instruction.detect,self.id,Config.serverId)
        self.server_disconnected=True
        time.sleep(Config.heartbeatRate)
        if self.server_disconnected:
            print('We temporarily lost contact with the server.')
            if not self.reconnect():
                self.stop()
    def reconnect(self,attempt=1):#死了，我来抢救！
        if attempt<=Config.maximumAttemptLimit:
            try:
                self.stop()
                self.running=True
                self._init_socket()
                self.send(Config.MessageType.inquire,Config.Instruction.call,self.id,Config.serverId)
                return True
            except Exception as error:
                print(f'Failed to reconnect to the server')
                time.sleep(5)
                self.reconnect(attempt+1)
        else:
            return False#你真死啦？！
