# coding=gbk
from fastapi import FastAPI
from pydantic import BaseModel
from Conversation import Conversation

app = FastAPI()

# ����һ�� Conversation ʵ��
conversation = Conversation(prompt="�����Ϻ�ֱ�������˾ѵ����һ�����ġ��Ѻá�רҵ����ҵ����֧�ֿͷ����ܹ�Ϊ�ͻ���ѯ�ض��Ĳ�Ʒ���Լ��Ϣ�������Ľ�����")

class ChatRequest(BaseModel):
    text: str

class ChatResponse(BaseModel):
    response: str

@app.post("/chat", response_model=ChatResponse)
def chat(chat_request: ChatRequest):
    # �������л�ȡ�û�������ı�
    user_input = chat_request.text

    # ʹ�� Conversation ʵ�������жԻ�
    response = conversation.ask(question=user_input)

    # �������ֵĻش�
    return {"response": response.content}

# ��Ӹ�·��
@app.get("/")
def read_root():
    return {"message": "��ӭ,����� /chat ҳ��������졣"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="192.168.200.57", port=8000)
