import socket
from config import Config,Instruction,MessageType,Error
from message import Message
class ServerSocket:
    def __init__(self):
        self._init_socket()
        self.current_give_id=1
        self.clients_dict:dict[str,socket.socket]={}
        self.address_dict={}
        self.running=True
    def _init_socket(self):
        self.socket=socket.socket(socket.AF_INET,socket.SOCK_STREAM)
        self.socket.bind((Config.host,Config.port))
        self.socket.listen()
    def stop(self):
        self.running=False
        self.socket.close()
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
            message=self.socket.recv(Config.maximum_text_limit)
            self.handle(Message.loads(message)) if Message.is_message(message) else None
        except socket.error as error:
            print(f'Error receiving message:{error}')
    def error_report(self,addressee,error_type):
        self.send(Message.dump(
            MessageType.report,
            Instruction.error,
            Config.server_id,
            addressee,
            error_type
        ))
    def heartbeat_detection(self,addressee):
        self.send(Message.dump(
            MessageType.detection,
            Instruction.detect,
            addressee,
            Config.server_id,
            ''
        ))
    def send_respond(self,instruction,addressee):
        self.send(Message.dump(
            MessageType.respond,
            instruction,
            Config.server_id,
            addressee,
            ''
        ))
    def handle(self,dictionary):
        if dictionary is not None and type(dictionary)==dict:
            match dictionary['type']:
                case MessageType.transmit:
                    match dictionary['instruction']:
                        case instruction if instruction in {
                            Instruction.text,
                            Instruction.file
                        }:
                            self.send(Message.dumps(dictionary))
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
                            match dictionary['addressee']:
                                case Config.server_id:
                                    self.heartbeat_detection(dictionary['sender'])
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
                            self.send(Message.dumps(dictionary))
                        case Instruction.please:
                            self.send_respond(Instruction.id,dictionary['sender'])
                        case Instruction.call:
                            self.send_respond(Instruction.known,dictionary['sender'])
                        case instruction if instruction in Instruction.difference({
                            Instruction.bye,
                            Instruction.please,
                            Instruction.call
                        }):
                            self.error_report(dictionary['sender'],Error.WrongInstruction)
                        case _:
                            self.error_report(dictionary['sender'],Error.InstructionNotExist)
                case MessageType.respond:
                    self.error_report(dictionary['sender'],Error.WrongMessageType)
                case MessageType.report:
                    match dictionary['instruction']:
                        case Instruction.error:
                            match dictionary['addressee']:
                                case Config.server_id:
                                    self.error_report(dictionary['sender'],Error.WrongAddressee)
                                case _:
                                    self.send(Message.dumps(dictionary))
                        case instruction if instruction in Instruction.difference({
                            Instruction.error
                        }):
                            self.error_report(dictionary['sender'],Error.WrongInstruction)
                        case _:
                            self.error_report(dictionary['sender'],Error.InstructionNotExist)
                case _:
                    self.error_report(dictionary['sender'],Error.MessageTypeNotExist)
    def send(self,message):
        dictionary=Message.loads(message)
        if dictionary is not None and type(dictionary)==dict:
            try:
                if dictionary['instruction']==Config.broadcast_id:
                    for id in self.clients_dict.keys():
                        if id==dictionary['sender']:
                            continue
                        SOCKET:socket.socket=self.clients_dict[id]
                        SOCKET.sendall(message)
                else:
                    for id in self.clients_dict.keys():
                        self.clients_dict[id].sendall(message)
            except socket.error as error:
                print(f'Error sending message to client {dictionary['addressee']}:{error}')
                del self.clients_dict[dictionary['addressee']]
                try:
                    self.error_report(dictionary['sender'],Error.AddresseeNotExist)
                except socket.error as error:
                    print(f'Error sending message to client {dictionary['sender']}:{error}')
                    del self.clients_dict[dictionary['sender']]
