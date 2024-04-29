#累死了，注释真难写
#和client_socket.py差不多啦，重复的我不会再提
import socket
from config import Config
from message import Message
class ServerSocket:
    def __init__(self):
        self._init_socket()
        self.current_give_id=1#开始编号id1
        self.clients_dict={}
        self.address_dict={}
        self.running=True
    def _init_socket(self):
        self.socket=socket.socket(socket.AF_INET,socket.SOCK_STREAM)
        self.socket.bind((Config.serverHost,Config.usingPort))#和客户端不一样的地方，就在于它是监听不是连接
        self.socket.listen()#一看就懂，我不说了
    def stop(self):
        self.running=False
        self.socket.close()
    #我们接收，我们编号，我们存储
    def accept(self):
        client_socket,address=self.socket.accept()
        print(f'A client socket, from {address}, connect to server...')
        if not self.address_dict[address]:
            ID=self.allocate()
            self.clients_dict[ID]=client_socket
            self.address_dict[address]=ID
    #id2333听令！
    def allocate(self)->str:
        ID=self.current_give_id
        self.current_give_id+=1
        return 'id'+str(ID)
    #发送，啊，对，是的，没错，和客户端的逻辑是一样的，就多了个找人的代码
    def send(self,type,instruction,sender,addressee,content=''):
        MESSAGE=Message.dumps(type,instruction,sender,addressee,content)
        #说的就是你，找人的代码！
        for id in self.clients_dict.keys():
            if addressee==id:
                TARGET_SOCKET:socket.socket=self.clients_dict[id]
        TARGET_SOCKET.sendall(MESSAGE)
    def receive(self):
        MESSAGE=self.socket.recv(Config.maximumTextLimit).decode()
        self.handle_receive(MESSAGE) if Message.is_message(MESSAGE) else None
    def handle_receive(self,message):
        if message is not None:
            DICTIONARY=Message.loads(message)
            if type(DICTIONARY)==dict:
                match DICTIONARY['type']:
                    case Config.MessageType.transmit:#哈哈哈！偷懒而已，既然有现成的，为什么还要自己一个一个Config.出来！
                        self.send(DICTIONARY['type'],DICTIONARY['instruction'],DICTIONARY['sender'],DICTIONARY['addressee'],DICTIONARY['content'])
                    case Config.MessageType.detection:
                        match DICTIONARY['instruction']:
                            case Config.Instruction.detect:
                                match DICTIONARY['addressee']:
                                    case Config.serverId:#交换了addressee和sender
                                        self.send(DICTIONARY['type'],DICTIONARY['instruction'],DICTIONARY['addressee'],DICTIONARY['sender'])
                    case Config.MessageType.inquire:
                        match DICTIONARY['instruction']:
                            case Config.Instruction.bye:#一模一样，不要看了
                                self.send(DICTIONARY['type'],DICTIONARY['instruction'],DICTIONARY['sender'],DICTIONARY['addressee'])
                                del self.clients_dict[DICTIONARY['sender']]
                            case Config.Instruction.please:
                                match DICTIONARY['addressee']:
                                    case Config.serverId:#真麻烦
                                        self.send(Config.MessageType.respond,Config.Instruction.id,Config.serverId,DICTIONARY['sender'],self.address_dict[DICTIONARY['sender']])
                            case Config.Instruction.call:
                                match DICTIONARY['addressee']:
                                    case Config.serverId:#这就方便了
                                        self.send(Config.MessageType.respond,Config.Instruction.known,Config.serverId,DICTIONARY['sender'])
