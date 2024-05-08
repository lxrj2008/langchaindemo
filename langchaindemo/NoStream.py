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
    user_input = input("you: ")  # 用户输入
    if user_input.lower() in ["exit", "quit", "bye"]:
        print("再见！")
        break  # 如果用户输入 exit、quit 或 bye，则退出循环
    current_time = datetime.now().strftime("%H:%M:%S")  # 获取当前系统时间
    print(f"[{current_time}] you: {user_input}")  # 打印用户输入及时间
    # 调用 OpenAI API 进行回复
    completion = client.chat.completions.create(
        model=cfg.ONLINE_LLM_MODEL["AzureOpenAI"]["model_name"],
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": user_input}
        ]
    )
    current_time = datetime.now().strftime("%H:%M:%S")  # 获取当前系统时间
    print(f"[{current_time}] Bot: {completion.choices[0].message.content}")  # 打印 AI 回答及时间
