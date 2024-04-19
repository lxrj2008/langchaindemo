
from fastapi import FastAPI
from pydantic import BaseModel
from Conversation import Conversation

app = FastAPI()

# 创建一个 Conversation 实例
conversation = Conversation()

class ChatRequest(BaseModel):
    text: str

class ChatResponse(BaseModel):
    response: str

@app.post("/chat", response_model=ChatResponse)
def chat(chat_request: ChatRequest):
    # 从请求中获取用户输入的文本
    user_input = chat_request.text

    # 使用 Conversation 实例来进行对话
    response = conversation.ask(question=user_input)

    # 返回助手的回答
    return {"response": response.content}

# 添加根路由
@app.get("/")
def read_root():
    return {"message": "欢迎,请访问 /chat 页面进行聊天。"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="192.168.200.57", port=8000)
