
import requests
from datetime import datetime
import cfg

# 定义 API 端点和密钥
api_base_url=cfg.ONLINE_LLM_MODEL["AzureOpenAI"]["api_base_url"]
api_version=cfg.ONLINE_LLM_MODEL["AzureOpenAI"]["api_version"]
api_key=cfg.ONLINE_LLM_MODEL["AzureOpenAI"]["api_key"]
model_name=cfg.ONLINE_LLM_MODEL["AzureOpenAI"]["model_name"]
url = f"{api_base_url}/openai/deployments/{model_name}/chat/completions?api-version={api_version}"


while True:
    # 用户输入问题
    user_input = input("You: ")
    
    # 准备要发送的 JSON 数据
    data = {
        "messages": [
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": user_input}
        ]
    }
    current_time = datetime.now().strftime("%H:%M:%S")  # 获取当前系统时间
    print(f"[{current_time}] You: {user_input}")  # 打印用户输入及时间
    # 发送 POST 请求
    response = requests.post(url, headers={"Content-Type": "application/json", "api-key": api_key}, json=data)
    
    # 解析响应并打印 AI 的回答
    if response.status_code == 200:
        response_data = response.json()
        ai_response = response_data["choices"][0]["message"]["content"]
        current_time = datetime.now().strftime("%H:%M:%S")  # 获取当前系统时间
        print(f"[{current_time}] Bot:", ai_response)
    else:
        print("请求失败:", response.text)

    # 如果用户输入 "exit"、"quit" 或 "bye"，则退出循环
    if user_input.lower() in ["exit", "quit", "bye"]:
        print("再见！")
        break
