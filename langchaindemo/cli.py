
from Conversation import Conversation

def chat_loop():
    conversation = Conversation(prompt="你是上海直达软件公司训练的一个耐心、友好、专业的企业技术支持客服，能够为客户查询特定的产品或合约信息。用中文交流！")
    while True:
        user_input = input("You: ")
        res=conversation.ask(question=f"{user_input}")



# Start the chat loop
chat_loop()
