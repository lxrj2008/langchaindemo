
from fastapi import FastAPI
from pydantic import BaseModel,constr
from Conversation import Conversation  
import uvicorn
import cfg

app = FastAPI()

class ChatRequest(BaseModel):
    question: constr(min_length=1,max_length=cfg.wordsnum) 
    username: constr(min_length=1,max_length=60) 

class ChatResponse(BaseModel):
    answer: str
    button: str

conversation_manager = {}

@app.post("/chat", response_model=ChatResponse,summary="Chat with Assistant", description="""请向助手提问吧.1、username必须要传，且是每个终端的值，切勿通过java api生成一个固定值传递
2、AIChatService需要通过这个username这个参数来维护每个终端的多轮对话信息，以达到每个终端的ask和answer不会互相影响的目的""")
async def chat(chat_request: ChatRequest):
    try:
        
        user_input = chat_request.question
        username = chat_request.username
        
       
        if username not in conversation_manager:
            conversation_manager[username] = Conversation(username)

        conversation = conversation_manager[username]
        response_message = conversation.ask(user_input) 
        return response_message
    
    except Exception as e:
        return cfg.inneralError



@app.get("/",summary="Root", description="欢迎进入直达AI助手api根目录")
async def read_root():
    return {"message": "Welcome, please visit /chat page to chat，api docs is host/docs"}

if __name__ == "__main__":
    
    uvicorn.run(app, host=cfg.hostinfo["hostname"], port=int(cfg.hostinfo["port"]))
