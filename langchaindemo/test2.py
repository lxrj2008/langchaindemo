# coding=gbk
import os
from openai import OpenAI
from openai import AzureOpenAI

os.environ["AZURE_OPENAI_KEY"] = 'd58136d46efe4cedb8e9c33d682d518f'#填写自己的Azure Api_key
client = AzureOpenAI(
    azure_endpoint = "https://zdopenai.openai.azure.com/", 
    api_key=os.environ.get("AZURE_OPENAI_KEY"),
    api_version="2024-02-15-preview"
)
stream = client.chat.completions.create(
    model="gpt-4",
    messages=[
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": "证明必达格拉斯定理"}
    ],
    stream=True,
)

for chunk in stream:
    if not chunk.choices or chunk.choices[0].delta.content is None:
        continue

    print(chunk.choices[0].delta.content, end="")
print()

