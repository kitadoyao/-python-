import socket
import time
from config import Config,Instruction,MessageType,Error
from message import Message
class ClientSocket:
    def __init__(self):
        self._init_socket()
        self.id=socket.gethostname()
        self.running=True
        self.server_disconnected=False
        self.send(MessageType.inquire,Instruction.please,self.id,Config.server_id)
    def _init_socket(self):
        try:
            self.running=True
            self.socket=socket.socket(socket.AF_INET,socket.SOCK_STREAM)
            self.socket.connect((Config.host,Config.port))
        except socket.error as error:
            print(f'Error connecting to the server:{error}')
    def stop(self):
        self.running=False
        self.socket.close()
    def send(self,type,instruction,sender,addressee,content=''):
        try:
            message=Message.dump(type,instruction,sender,addressee,content)
            self.socket.sendall(message)
        except socket.error as error:
            print(f'Error sending message:{error}')
            if not self.reconnect():
                self.stop()
    def handle_send(self,message):
        dictionary=Message.loads(message)
        if dictionary is not None and type(dictionary)==dict:
            if dictionary['instruction']==Instruction.bye:
                self.stop()
    def receive(self):
        try:
            message=self.socket.recv(Config.maximum_text_limit)
            self.handle_receive(Message.loads(message)) if Message.is_message(message) else None
        except socket.error as error:
            print(f'Error receiving message:{error}')
            if not self.reconnect():
                self.stop()
    def error_report(self,addressee,error_type):
        self.send(
            MessageType.report,
            Instruction.error,
            self.id,
            addressee,
            error_type
        )
    def handle_receive(self,dictionary):
        if dictionary is not None and type(dictionary)==dict:
            match dictionary['type']:
                case MessageType.transmit:
                    match dictionary['instruction']:
                        case Instruction.text:
                            print(f'{dictionary['sender']}:{dictionary['content']}')
                        case Instruction.file:
                            filename=dictionary['content']['filename']
                            file_content=dictionary['content']['file_content']
                            with open(filename,'w') as file:
                                file.write(file_content)
                        case instruction if instruction in Instruction.difference({
                            Instruction.text,
                            Instruction.file
                        }):
                            self.error_report(dictionary['sender'],Error.WrongInstruction)
                        case _:
                            self.error_report(dictionary['sender'],Error.InstructionNotExist)
                case MessageType.detection:
                    match dictionary['instruction']:
                        case Instruction.detect:
                            match dictionary['sender']:
                                case Config.server_id:
                                    self.server_disconnected=False
                                case _:
                                    self.error_report(dictionary['sender'],Error.WrongAddressee)
                        case instruction if instruction in Instruction.difference({
                            Instruction.detect
                        }):
                            self.error_report(dictionary['sender'],Error.WrongInstruction)
                        case _:
                            self.error_report(dictionary['sender'],Error.InstructionNotExist)
                case MessageType.inquire:
                    match dictionary['instruction']:
                        case Instruction.bye:
                            print(f'{dictionary['sender']}:Communication stopped')
                        case instruction if instruction in Instruction.difference({
                            Instruction.bye
                        }):
                            self.error_report(dictionary['sender'],Error.WrongInstruction)
                        case _:
                            self.error_report(dictionary['sender'],Error.InstructionNotExist)
                case MessageType.respond:
                    match dictionary['instruction']:
                        case Instruction.id:
                            match dictionary['sender']:
                                case Config.server_id:
                                    self.id=dictionary["content"]
                                    print(f'You\'ve been assigned:{dictionary["content"]}')
                                case _:
                                    self.error_report(dictionary['sender'],Error.WrongAddressee)
                        case Instruction.known:
                            match dictionary['sender']:
                                case Config.server_id:
                                    print('You reconnected to the server.')
                                case _:
                                    self.error_report(dictionary['sender'],Error.WrongAddressee)
                        case instruction if instruction in Instruction.difference({
                            Instruction.id,
                            Instruction.known
                        }):
                            self.error_report(dictionary['sender'],Error.WrongInstruction)
                        case _:
                            self.error_report(dictionary['sender'],Error.InstructionNotExist)
                case MessageType.report:
                    match dictionary['instruction']:
                        case Instruction.error:
                            print(f'An error occurs:{dictionary["content"]}')
                        case instruction if instruction in Instruction.difference({
                            Instruction.error
                        }):
                            self.error_report(dictionary['sender'],Error.WrongInstruction)
                        case _:
                            self.error_report(dictionary['sender'],Error.InstructionNotExist)
                case _:
                    self.error_report(dictionary['sender'],Error.MessageTypeNotExist)
    def heartbeat(self):
        self.send(MessageType.detection,Instruction.detect,self.id,Config.server_id)
        self.server_disconnected=True
        time.sleep(Config.heartbeat_rate)
        if self.server_disconnected:
            print('We temporarily lost contact with the server.')
            if not self.reconnect():
                self.stop()
    def reconnect(self):
        attempt=1
        while True:
            if attempt>Config.maximum_attempt_limit:
                break
            try:
                self.stop()
                self._init_socket()
                self.send(MessageType.inquire,Instruction.call,self.id,Config.server_id)
                return True
            except Exception as error:
                print(f'Failed to reconnect to the server:{error}')
                attempt+=1
                time.sleep(Config.wait_attempt_rate)
                print(f'Failed to reconnect to the server')
                time.sleep(5)
                self.reconnect(attempt+1)
        else:
            return False#你真死啦？！
