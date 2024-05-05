import socket
from config import Config
from message import Message
class ServerSocket:
    def __init__(self):
        self.config=Config()
        self._init_socket()
        self.current_give_id=1
        self.clients_dict:dict[str,socket.socket]={}
        self.address_dict={}
        self.running=True
    def _init_socket(self):
        self.socket=socket.socket(socket.AF_INET,socket.SOCK_STREAM)
        self.socket.bind((self.config.host,self.config.port))
        self.socket.listen()
    def close(self):
        self.running=False
        self.socket.close()
        for clients_socket in self.clients_dict.values():
            clients_socket.close()
    def accept(self):
        try:
            client_socket,address=self.socket.accept()
            print(f'A client socket, from {address}, connect to server...')
            if address not in self.address_dict:
                id=self.allocate()
                self.clients_dict[id]=client_socket
                self.address_dict[address]=id
        except socket.error as error:
            print(f'Error accepting client connection:{error}')
    def allocate(self)->str:
        id=self.current_give_id
        self.current_give_id+=1
        return 'id'+str(id)
    def receive(self):
        try:
            message=self.socket.recv(self.config.maximum_text_limit)
            self.handle(Message.loads(message)) if Message.is_message(message) else None
        except socket.error as error:
            print(f'Error receiving message:{error}')
    def error_report(self,addressee,error_type):
        self.send(Message.dump(
            self.config.message_type.report,
            self.config.instruction.error,
            self.config.server_id,
            addressee,
            error_type
        ))
    def heartbeat_detection(self,addressee):
        self.send(Message.dump(
            self.config.message_type.detection,
            self.config.instruction.detect,
            addressee,
            self.config.server_id,
            ''
        ))
    def send_respond(self,instruction,addressee):
        self.send(Message.dump(
            self.config.message_type.respond,
            instruction,
            self.config.server_id,
            addressee,
            ''
        ))
    def handle(self,dictionary):
        if dictionary is not None and type(dictionary)==dict:
            match dictionary['type']:
                case self.config.message_type.transmit:
                    match dictionary['instruction']:
                        case instruction if instruction in {
                            self.config.instruction.text,
                            self.config.instruction.file
                        }:
                            self.send(Message.dumps(dictionary))
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
                            match dictionary['addressee']:
                                case self.config.server_id:
                                    self.heartbeat_detection(dictionary['sender'])
                                case _:
                                    self.error_report(dictionary['sender'],self.config.error.WrongAddressee)
                        case instruction if instruction in self.config.instruction.difference({
                            self.config.instruction.detect
                        }):
                            self.error_report(dictionary['sender'],self.config.error.WrongInstruction)
                        case _:
                            self.error_report(dictionary['sender'],self.config.error.InstructionNotExist)
                case self.config.message_type.inquire:
                    match dictionary['instruction']:
                        case self.config.instruction.bye:
                            self.send(Message.dumps(dictionary))
                        case self.config.instruction.join:
                            match dictionary['addressee']:
                                case self.config.server_id:
                                    self.send_respond(self.config.instruction.id,dictionary['sender'])
                                case _:
                                    self.error_report(dictionary['sender'],self.config.error.WrongAddressee)
                        case self.config.instruction.call:
                            match dictionary['addressee']:
                                case self.config.server_id:
                                    self.send_respond(self.config.instruction.known,dictionary['sender'])
                                case _:
                                    self.error_report(dictionary['sender'],self.config.error.WrongAddressee)
                        case instruction if instruction in self.config.instruction.difference({
                            self.config.instruction.bye,
                            self.config.instruction.join,
                            self.config.instruction.call
                        }):
                            self.error_report(dictionary['sender'],self.config.error.WrongInstruction)
                        case _:
                            self.error_report(dictionary['sender'],self.config.error.InstructionNotExist)
                case self.config.message_type.respond:
                    self.error_report(dictionary['sender'],self.config.error.WrongMessageType)
                case self.config.message_type.report:
                    match dictionary['instruction']:
                        case self.config.instruction.error:
                            match dictionary['addressee']:
                                case self.config.server_id:
                                    self.error_report(dictionary['sender'],self.config.error.WrongAddressee)
                                case _:
                                    self.send(Message.dumps(dictionary))
                        case instruction if instruction in self.config.instruction.difference({
                            self.config.instruction.error
                        }):
                            self.error_report(dictionary['sender'],self.config.error.WrongInstruction)
                        case _:
                            self.error_report(dictionary['sender'],self.config.error.InstructionNotExist)
                case _:
                    self.error_report(dictionary['sender'],self.config.error.MessageTypeNotExist)
    def send(self,message):
        dictionary=Message.loads(message)
        if dictionary is not None:
            try:
                if dictionary['addressee']==self.config.broadcast_id:
                    for client_id,client_socket in self.clients_dict.items():
                        if client_id==dictionary['sender']:
                            continue
                        client_socket.sendall(message)
                else:
                    for id in self.clients_dict.keys():
                        self.clients_dict[id].sendall(message)
            except socket.error as error:
                if dictionary['addressee']==self.config.broadcast_id:
                    print(f'Error sending broadcast to client {client_id}:{error}')
                    del self.clients_dict[client_id]
                    self.error_sending(dictionary['sender'])
                else:
                    print(f'Error sending message to client {dictionary['addressee']}:{error}')
                    del self.clients_dict[dictionary['addressee']]
                    self.error_sending(dictionary['sender'])
    def error_sending(self,sender):
        try:
            self.error_report(sender,self.config.error.AddresseeNotExist)
        except socket.error as error:
            print(f'Error sending message to client {sender}:{error}')
            del self.clients_dict[sender]
