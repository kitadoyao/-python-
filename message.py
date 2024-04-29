#引入json模块
import json
#定义Message类
class Message:
    #这告诉你，这是一个静态方法
    #什么是静态方法？
    #Message.dumps()这样用，就是静态方法
    #self.message=Message()
    #self.message.dumps()这样用就不是静态方法
    #具体来说，就是方便【摆烂...】
    #其实是因为我们不需要访问对象属性，也就是self开头的属性的方法，我们完全可以用静态方法
    #方便...
    @staticmethod
    #序列化为json对象
    #是读序列化吧？忘了
    #就是把python的dict对象转成json对象
    #众所周知，json是字符串
    #你不知道？我现在告诉你了【乐】
    #其实就是形如'{"key":"value"}'的字符串就是json对象
    def dumps(msg_type,instruction,sender,addressee,content):
        DICTIONARY={
            "type":msg_type,#消息类型
            "instruction":instruction,#指令
            "sender":sender,#发送者
            "addressee":addressee,#接收者
            "content":content,#内容
        }
        #实际上写成这样，是因为【我太难了...】
        #你想，消息格式搞得一点都不同
        #接收信息怎么解析都成问题
        #有谁？没有谁？
        #所以在不得已的情况下，高出一堆消息类型和指令
        #------
        #这里用的是json的dumps()函数，把字典转成json
        #你问我是不是脱裤子放屁————多此一举?
        #一个字，方便【摆烂...】
        #你想想，一个文件里，引入太多模块，是不是很乱
        #一下用这个，一下用哪个的【汗颜...】
        return json.dumps(DICTIONARY).encode()
    @staticmethod
    #懂的都懂，不懂的我解释一下
    #为什么要写一个判断是不是message的？
    #好看啊？！【乐】
    def is_message(message):
        TEMPLATE={"type","instruction","sender","addressee","content"}
        try:
            DICTIONARY=json.loads(message)
            if type(DICTIONARY)==dict:
                return set(DICTIONARY.keys())==TEMPLATE
        except json.JSONDecodeError:
            return False
    @staticmethod
    #不用解释了，包装一下【摆烂...】
    def loads(message):
        if Message.is_message(message):
            return json.loads(message)
