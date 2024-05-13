import os
from openai import AzureOpenAI
import cfg
from datetime import datetime

os.environ["AZURE_OPENAI_API_KEY"] = cfg.ONLINE_LLM_MODEL["AzureOpenAI"]["api_key"]
os.environ["OPENAI_API_VERSION"] = cfg.ONLINE_LLM_MODEL["AzureOpenAI"]["api_version"]
os.environ["AZURE_OPENAI_ENDPOINT"] = cfg.ONLINE_LLM_MODEL["AzureOpenAI"]["api_base_url"]
client = AzureOpenAI()

while True:
    current_time = datetime.now().strftime("%H:%M:%S")
    user_input = input("you: ")  
    if user_input.lower() in ["exit", "quit", "bye"]:
        print("再见！")
        break  
    current_time = datetime.now().strftime("%H:%M:%S") 
    print(f"[{current_time}] you: {user_input}")  

    completion = client.chat.completions.create(
        model=cfg.ONLINE_LLM_MODEL["AzureOpenAI"]["model_name"],
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": user_input}
        ]
    )
    current_time = datetime.now().strftime("%H:%M:%S")  
    print(f"[{current_time}] Bot: {completion.choices[0].message.content}")  
