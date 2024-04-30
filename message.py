import json
class Message:
    @staticmethod
    def dump(msg_type,instruction,sender,addressee,content)->bytes:
        dictionary={
            "type":msg_type,
            "instruction":instruction,
            "sender":sender,
            "addressee":addressee,
            "content":content,
        }
        return json.dumps(dictionary).encode()
    @staticmethod
    def dumps(dictionary:dict)->bytes:
        return json.dumps(dictionary).encode()
    @staticmethod
    def is_message(message)->bool:
        TEMPLATE={"type","instruction","sender","addressee","content"}
        try:
            dictionary:dict=json.loads(message)
            return set(dictionary.keys())==TEMPLATE
        except json.JSONDecodeError:
            return False
    @staticmethod
    def loads(message:bytes)->dict|None:
        if Message.is_message(message):
            return json.loads(message)
        else:
            return None 
