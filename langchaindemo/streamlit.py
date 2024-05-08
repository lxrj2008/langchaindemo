import os
from openai import AzureOpenAI
import cfg

os.environ["AZURE_OPENAI_API_KEY"] = cfg.ONLINE_LLM_MODEL["AzureOpenAI"]["api_key"]
os.environ["OPENAI_API_VERSION"] = cfg.ONLINE_LLM_MODEL["AzureOpenAI"]["api_version"]
os.environ["AZURE_OPENAI_ENDPOINT"] = cfg.ONLINE_LLM_MODEL["AzureOpenAI"]["api_base_url"]
client = AzureOpenAI()

while True:
    user_input = input("you: ")  # 用户输入
    if user_input.lower() in ["exit", "quit", "bye"]:
        print("再见！")
        break  # 如果用户输入 exit、quit 或 bye，则退出循环
    # 调用 OpenAI API 进行回复
    stream = client.chat.completions.create(
        model=cfg.ONLINE_LLM_MODEL["AzureOpenAI"]["model_name"],
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": user_input}
        ],
        stream=True,
    )
    for chunk in stream:
        if not chunk.choices or chunk.choices[0].delta.content is None:
            continue
        response = chunk.choices[0].delta.content
        print(chunk.choices[0].delta.content, end="")
    print()
