
import requests
from datetime import datetime
import cfg

api_base_url=cfg.ONLINE_LLM_MODEL["AzureOpenAI"]["api_base_url"]
api_version=cfg.ONLINE_LLM_MODEL["AzureOpenAI"]["api_version"]
api_key=cfg.ONLINE_LLM_MODEL["AzureOpenAI"]["api_key"]
model_name=cfg.ONLINE_LLM_MODEL["AzureOpenAI"]["model_name"]
url = f"{api_base_url}/openai/deployments/{model_name}/chat/completions?api-version={api_version}"


while True:

    user_input = input("You: ")
    

    data = {
        "messages": [
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": user_input}
        ]
    }
    current_time = datetime.now().strftime("%H:%M:%S")  
    print(f"[{current_time}] You: {user_input}")  
    
    response = requests.post(url, headers={"Content-Type": "application/json", "api-key": api_key}, json=data)
    
    
    if response.status_code == 200:
        response_data = response.json()
        ai_response = response_data["choices"][0]["message"]["content"]
        current_time = datetime.now().strftime("%H:%M:%S")  
        print(f"[{current_time}] Bot:", ai_response)
    else:
        print("请求失败:", response.text)

    
    if user_input.lower() in ["exit", "quit", "bye"]:
        print("再见！")
        break
