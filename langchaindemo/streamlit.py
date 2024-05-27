import os
from fastapi import FastAPI
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, constr
from openai import AzureOpenAI
import cfg
from fastapi.middleware.cors import CORSMiddleware
# 配置环境变量
os.environ["AZURE_OPENAI_API_KEY"] = cfg.ONLINE_LLM_MODEL["AzureOpenAI"]["api_key"]
os.environ["OPENAI_API_VERSION"] = cfg.ONLINE_LLM_MODEL["AzureOpenAI"]["api_version"]
os.environ["AZURE_OPENAI_ENDPOINT"] = cfg.ONLINE_LLM_MODEL["AzureOpenAI"]["api_base_url"]

client = AzureOpenAI()

app = FastAPI()

# 添加 CORS 中间件
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 允许所有源
    allow_credentials=True,
    allow_methods=["POST"],  # 允许的 HTTP 方法
    allow_headers=["*"],  # 允许所有标头
)
# 定义请求模型
class ChatRequest(BaseModel):
    question: constr(min_length=1, max_length=cfg.wordsnum)
    username: constr(min_length=1, max_length=60)

@app.post("/chat")
async def chat(request: ChatRequest):
    question = request.question
    username = request.username

    def generate_response():
        stream = client.chat.completions.create(
            model=cfg.ONLINE_LLM_MODEL["AzureOpenAI"]["model_name"],
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": f"{question}"}
            ],
            stream=True,
        )

        for chunk in stream:
            if not chunk.choices or chunk.choices[0].delta.content is None:
                continue
            response = chunk.choices[0].delta.content
            yield response

    return StreamingResponse(generate_response(), media_type="text/plain")

# 启动FastAPI应用
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="192.168.200.57", port=8001)
