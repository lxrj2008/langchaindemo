from Conversation import Conversation

def chat_loop():
    try:
        conversation = Conversation('device01')
        while True:
            user_input = input("\nYou: ")
            res = conversation.ask(question=f"{user_input}")
            print("\nBot：", res.content)
    
    except Exception as e:
        print("An error occurred:", e)

# Start the chat loop
chat_loop()
