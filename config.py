import configparser
CONFIG=configparser.ConfigParser()
CONFIG.read('config.ini')
class Config:
    host=CONFIG.get('SERVER','host')
    port=CONFIG.getint('SERVER','port')
    server_id=CONFIG.get('SERVER','id')
    broadcast_id=CONFIG.get('CLIENT','all_members_id')
    heartbeat_rate=CONFIG.getint('CLIENT','heartbeat_rate')
    wait_attempt_rate=CONFIG.getint('CLIENT','wait_attempt_rate')
    maximum_attempt_limit=CONFIG.getint('CLIENT','maximum_attempt_limit')
    maximum_text_limit=CONFIG.getint('TEXT','maximum_text_limit')
class MessageType:
        transmit=CONFIG.get('MESSAGE_TYPES','transmit')
        detection=CONFIG.get('MESSAGE_TYPES','detection')
        inquire=CONFIG.get('MESSAGE_TYPES','inquire')
        respond=CONFIG.get('MESSAGE_TYPES','respond')
        report=CONFIG.get('MESSAGE_TYPES','report')
class Instruction:
        text=CONFIG.get('INSTRUCTIONS','send_text')
        file=CONFIG.get('INSTRUCTIONS','send_file')
        error=CONFIG.get('INSTRUCTIONS','send_error')
        bye=CONFIG.get('INSTRUCTIONS','end_communication')
        please=CONFIG.get('INSTRUCTIONS','request_to_join')
        id=CONFIG.get('INSTRUCTIONS','allocation_id')
        call=CONFIG.get('INSTRUCTIONS','request_reconnection')
        known=CONFIG.get('INSTRUCTIONS','successfull_reconnection')
        detect=CONFIG.get('INSTRUCTIONS','heartbeat_detection')
        @staticmethod
        def difference(A:set):
            B={
                Instruction.text,
                Instruction.file,
                Instruction.error,
                Instruction.bye,
                Instruction.please,
                Instruction.id,
                Instruction.call,
                Instruction.known,
                Instruction.detect
            }
            C:set=B.difference(A)
            return C
class Error:
        AddresseeNotExist=CONFIG.get('ERROR','AddresseeNotExist')
        InstructionNotExist=CONFIG.get('ERROR','InstructionNotExist')
        MessageTypeNotExist=CONFIG.get('ERROR','MessageTypeNotExist')
        WrongAddressee=CONFIG.get('ERROR','WrongAddressee')
        WrongInstruction=CONFIG.get('ERROR','WrongInstruction')
        WrongMessageType=CONFIG.get('ERROR','WrongMessageType')
