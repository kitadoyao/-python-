import socket
import time
from config import Config
from message import Message
class ClientSocket:
    def __init__(self):
        self.config=Config()
        self._init_socket()
        self.id=socket.gethostname()
        self.running=True
        self.server_disconnected=False
        self.send(self.config.message_type.inquire,self.config.instruction.join,self.id,self.config.server_id)
    def _init_socket(self):
        try:
            self.running=True
            self.socket=socket.socket(socket.AF_INET,socket.SOCK_STREAM)
            self.socket.connect((self.config.host,self.config.port))
        except socket.error as error:
            print(f'Error connecting to the server:{error}')
    def close(self):
        self.running=False
        self.socket.close()
    def send(self,msg_type,instruction,sender,addressee,content=''):
        try:
            message:bytes=Message.dump(msg_type,instruction,sender,addressee,content)
            self.socket.sendall(message)
        except socket.error as error:
            print(f'Error sending message:{error}')
            if not self.reconnect():
                self.close()
    def handle_send(self,message):
        dictionary=Message.loads(message)
        if dictionary is not None and type(dictionary)==dict:
            if dictionary['instruction']==self.config.instruction.bye:
                self.close()
    def receive(self):
        try:
            message=self.socket.recv(self.config.maximum_text_limit)
            if Message.is_message(message):
                self.handle_receive(Message.loads(message))
        except socket.error as error:
            print(f'Error receiving message:{error}')
            if not self.reconnect():
                self.close()
    def error_report(self,addressee,error_type):
        self.send(
            self.config.message_type.report,
            self.config.instruction.error,
            self.id,
            addressee,
            error_type
        )
    def handle_receive(self,dictionary):
        if dictionary is not None and type(dictionary)==dict:
            match dictionary['type']:
                case self.config.message_type.transmit:
                    match dictionary['instruction']:
                        case self.config.instruction.text:
                            print(f'{dictionary['sender']}:{dictionary['content']}')
                        case self.config.instruction.file:
                            filename=dictionary['content']['filename']
                            file_content=dictionary['content']['file_content']
                            with open(filename,'w') as file:
                                file.write(file_content)
                        case instruction if instruction in self.config.instruction.difference({
                            self.config.instruction.text,
                            self.config.instruction.file
                        }):
                            self.error_report(dictionary['sender'],self.config.error.WrongInstruction)
                        case _:
                            self.error_report(dictionary['sender'],self.config.error.InstructionNotExist)
                case self.config.message_type.detection:
                    match dictionary['instruction']:
                        case self.config.instruction.detect:
                            match dictionary['sender']:
                                case self.config.server_id:
                                    self.server_disconnected=False
                                case _:
                                    self.error_report(dictionary['sender'],self.config.error.WrongAddressee)
                        case instruction if instruction in instruction.difference({
                            self.config.instruction.detect
                        }):
                            self.error_report(dictionary['sender'],self.config.error.WrongInstruction)
                        case _:
                            self.error_report(dictionary['sender'],self.config.error.InstructionNotExist)
                case self.config.message_type.inquire:
                    match dictionary['instruction']:
                        case self.config.instruction.bye:
                            print(f'{dictionary['sender']}:Communication stopped')
                        case instruction if instruction in self.config.instruction.difference({
                            self.config.instruction.bye
                        }):
                            self.error_report(dictionary['sender'],self.config.error.WrongInstruction)
                        case _:
                            self.error_report(dictionary['sender'],self.config.error.InstructionNotExist)
                case self.config.message_type.respond:
                    match dictionary['instruction']:
                        case self.config.instruction.id:
                            match dictionary['sender']:
                                case self.config.server_id:
                                    self.id=dictionary["content"]
                                    print(f'You\'ve been assigned:{dictionary["content"]}')
                                case _:
                                    self.error_report(dictionary['sender'],self.config.error.WrongAddressee)
                        case self.config.instruction.known:
                            match dictionary['sender']:
                                case self.config.server_id:
                                    print('You reconnected to the server.')
                                case _:
                                    self.error_report(dictionary['sender'],self.config.error.WrongAddressee)
                        case instruction if instruction in instruction.difference({
                            self.config.instruction.id,
                            self.config.instruction.known
                        }):
                            self.error_report(dictionary['sender'],self.config.error.WrongInstruction)
                        case _:
                            self.error_report(dictionary['sender'],self.config.error.InstructionNotExist)
                case self.config.message_type.report:
                    match dictionary['instruction']:
                        case self.config.instruction.error:
                            print(f'An error occurs:{dictionary["content"]}')
                        case instruction if instruction in instruction.difference({
                            self.config.instruction.error
                        }):
                            self.error_report(dictionary['sender'],self.config.error.WrongInstruction)
                        case _:
                            self.error_report(dictionary['sender'],self.config.error.InstructionNotExist)
                case _:
                    self.error_report(dictionary['sender'],self.config.error.MessageTypeNotExist)
    def heartbeat(self):
        self.send(self.config.message_type.detection,self.config.instruction.detect,self.id,self.config.server_id)
        self.server_disconnected=True
        time.sleep(self.config.heartbeat_rate)
        if self.server_disconnected:
            print('We temporarily lost contact with the server.')
            if not self.reconnect():
                self.close()
    def reconnect(self):
        attempt=1
        while True:
            if attempt>self.config.maximum_attempt_limit:
                break
            try:
                self.close()
                self._init_socket()
                self.send(self.config.message_type.inquire,self.config.instruction.call,self.id,self.config.server_id)
                return True
            except Exception as error:
                print(f'Failed to reconnect to the server:{error}')
                attempt+=1
                time.sleep(self.config.wait_attempt_rate)
