
from zp_conversation import ZPConversation
from datetime import datetime

def chat_loop():
    try:
        conversation = ZPConversation('device01')
        while True:
            user_input = input("\nYou: ")
            current_time = datetime.now().strftime("%H:%M:%S")  
            print(f"[{current_time}] you: {user_input}")  
            res = conversation.ask(question=f"{user_input}")
            current_time = datetime.now().strftime("%H:%M:%S")  
            print(f"[{current_time}] Bot: {res['answer']}")  
    
    except Exception as e:
        print("An error occurred:", e)

chat_loop()
