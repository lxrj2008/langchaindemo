
from fastapi import FastAPI
from pydantic import BaseModel,constr
from Conversation import Conversation  
import uvicorn
import cfg

app = FastAPI()

class ChatRequest(BaseModel):
    question: constr(max_length=cfg.wordsnum) 
    username: constr(min_length=1) 

class ChatResponse(BaseModel):
    response: str

conversation_manager = {}

@app.post("/chat", response_model=ChatResponse)
async def chat(chat_request: ChatRequest):
    try:
        # 从请求中获取用户输入的文本和用户名
        user_input = chat_request.question
        username = chat_request.username
        
        # 检查是否已经为该用户名创建了 Conversation 实例，如果没有则创建一个
        if username not in conversation_manager:
            conversation_manager[username] = Conversation(username)

        conversation = conversation_manager[username]
        response_message = conversation.ask(user_input) 

        # 返回助手的回答
        return {"response": response_message.content}
    
    except Exception as e:
        return cfg.inneralError


# 添加根路由
@app.get("/")
async def read_root():
    return {"message": "Welcome, please visit /chat page to chat，api docs is host/docs"}

if __name__ == "__main__":
    
    uvicorn.run(app, host=cfg.hostinfo["hostname"], port=int(cfg.hostinfo["port"]))
