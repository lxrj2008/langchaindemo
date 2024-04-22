
import os
from openai import AzureOpenAI
import cfg

os.environ["AZURE_OPENAI_API_KEY"] = cfg.ONLINE_LLM_MODEL["AzureOpenAI"]["api_key"]
os.environ["OPENAI_API_VERSION"] = cfg.ONLINE_LLM_MODEL["AzureOpenAI"]["api_version"]
os.environ["AZURE_OPENAI_ENDPOINT"] = cfg.ONLINE_LLM_MODEL["AzureOpenAI"]["api_base_url"]
client = AzureOpenAI()
stream = client.chat.completions.create(
    model=cfg.ONLINE_LLM_MODEL["AzureOpenAI"]["model_name"],
    messages=[
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": "你好"}
    ],
    stream=True,
)

for chunk in stream:
    if not chunk.choices or chunk.choices[0].delta.content is None:
        continue

    print(chunk.choices[0].delta.content, end="")
print()

