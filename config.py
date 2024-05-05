from config_manager import ConfigManager
class Config:
    def __init__(self):
        self.host=ConfigManager.get('server','host')
        self.port=int(ConfigManager.get('server','port'))
        self.server_id=ConfigManager.get('server','server_id')
        self.broadcast_id=ConfigManager.get('client','broadcast_id')
        self.heartbeat_rate=int(ConfigManager.get('client','heartbeat_rate'))
        self.wait_attempt_rate=int(ConfigManager.get('client','wait_attempt_rate'))
        self.maximum_attempt_limit=int(ConfigManager.get('client','maximum_attempt_limit'))
        self.maximum_text_limit=int(ConfigManager.get('text','maximum_text_limit'))
        self.message_type=MessageType()
        self.instruction=Instruction()
        self.error=Error()
class MessageType:
    def __init__(self):
        self.transmit=ConfigManager.get('message_type','transmit')
        self.detection=ConfigManager.get('message_type','detection')
        self.inquire=ConfigManager.get('message_type','inquire')
        self.respond=ConfigManager.get('message_type','respond')
        self.report=ConfigManager.get('message_type','report')
class Instruction:
    def __init__(self):
        self.text=ConfigManager.get('instruction','send_text')
        self.file=ConfigManager.get('instruction','send_file')
        self.error=ConfigManager.get('instruction','send_error')
        self.bye=ConfigManager.get('instruction','end_communication')
        self.join=ConfigManager.get('instruction','request_to_join')
        self.id=ConfigManager.get('instruction','allocation_id')
        self.call=ConfigManager.get('instruction','request_reconnection')
        self.known=ConfigManager.get('instruction','successfull_reconnection')
        self.detect=ConfigManager.get('instruction','heartbeat_detection')
    def difference(self,A:set):
        B={
            self.text,
            self.file,
            self.error,
            self.bye,
            self.join,
            self.id,
            self.call,
            self.known,
            self.detect
        }
        C:set=B.difference(A)
        return C
class Error:
    def __init__(self):
        self.AddresseeNotExist=ConfigManager.get('error','AddresseeNotExist')
        self.InstructionNotExist=ConfigManager.get('error','InstructionNotExist')
        self.MessageTypeNotExist=ConfigManager.get('error','MessageTypeNotExist')
        self.WrongAddressee=ConfigManager.get('error','WrongAddressee')
        self.WrongInstruction=ConfigManager.get('error','WrongInstruction')
        self.WrongMessageType=ConfigManager.get('error','WrongMessageType')
        InstructionNotExist=CONFIG.get('ERROR','InstructionNotExist')
        MessageTypeNotExist=CONFIG.get('ERROR','MessageTypeNotExist')
        WrongAddressee=CONFIG.get('ERROR','WrongAddressee')
        WrongInstruction=CONFIG.get('ERROR','WrongInstruction')
        WrongMessageType=CONFIG.get('ERROR','WrongMessageType')
