
from Conversation import Conversation

def chat_loop():
    conversation = Conversation()
    while True:
        user_input = input("\nYou: ")
        res=conversation.ask(question=f"{user_input}")
        print("\nBot：", res.content)


# Start the chat loop
chat_loop()
