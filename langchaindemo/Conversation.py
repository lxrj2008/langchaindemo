
from openai import AzureOpenAI
import os,json,pyodbc,copy
import cfg,embedding
from collections import deque

os.environ["AZURE_OPENAI_API_KEY"] = cfg.ONLINE_LLM_MODEL["AzureOpenAI"]["api_key"]
os.environ["OPENAI_API_VERSION"] = cfg.ONLINE_LLM_MODEL["AzureOpenAI"]["api_version"]
os.environ["AZURE_OPENAI_ENDPOINT"] = cfg.ONLINE_LLM_MODEL["AzureOpenAI"]["api_base_url"]

class Conversation:
    def __init__(self,username=None):
        self.client = AzureOpenAI()
        self.username=username
        self.tools=cfg.tools
        self.messages = deque(copy.deepcopy(cfg.SystemPrompt))#first in first out queue
        self.round=0;
        

    def ask(self,question):
        try:
            self.messages.append({"role": "user", "content": question})
            response = self.client.chat.completions.create(
                model=cfg.ONLINE_LLM_MODEL["AzureOpenAI"]["model_name"],
                messages=self.messages,
                tools=self.tools,
                tool_choice="auto",
                temperature=cfg.CompleteionsPara["temperature"],
                max_tokens=cfg.CompleteionsPara["max_tokens"]
            )
            response_message = response.choices[0].message
            tool_calls = response_message.tool_calls
            if tool_calls:
                self.messages.append(response_message)
                for tool_call in tool_calls:
                    function_name = tool_call.function.name
                    function_result = {}
                    args = tool_call.function.arguments
                    if function_name == "get_contract_info":
                        
                        function_response = get_contract_info(**json.loads(args))
                    
                    elif function_name=="answer_question" :
                        function_response=answer_question(**json.loads(args))
                    else:
                        function_response = answer_question(**json.loads(args))
                        
                    self.messages.append(
                       {
                            "tool_call_id": tool_call.id,
                            "role": "tool",
                            "name": function_name,
                            "content": cfg.ToolPrompt.replace("knowledge", function_response).replace("question", question)
                            #"content": f"{function_response},以json格式输出",
                       }
                    )
                second_response = self.client.chat.completions.create(
                model=cfg.ONLINE_LLM_MODEL["AzureOpenAI"]["model_name"],
                messages=self.messages,
                #response_format={ "type": "json_object" },
                temperature=cfg.CompleteionsPara["temperature"],
                max_tokens=cfg.CompleteionsPara["max_tokens"])
                response_message = second_response.choices[0].message
            else:
                pass
            self.messages.append({"role": "assistant", "content": response_message.content})
            self.round += 1
            if self.round >= cfg.ChatRound:
               # 弹出前三个元素并保存
               first_three_messages = [self.messages.popleft() for _ in range(len(cfg.SystemPrompt))]
               # 计数器，用于跟踪完成的消息聊天轮数
               user_count = 0
               # 遍历队列中的元素
               while self.messages:
                   # 获取队列中的下一个元素
                   msg = self.messages.popleft()
                   # 如果遇到用户角色消息，则增加计数器
                   if isinstance(msg, dict) and msg.get("role") == "user":
                       user_count += 1
                   # 如果用户角色消息数量达到了2，则停止循环，并且把下一个role等于user的元素加回队列
                   if user_count == 2:
                       self.messages.appendleft(msg)
                       break
               # 将前三个元素放回队列，并且位置不变
               for mymsg in reversed(first_three_messages):
                   self.messages.appendleft(mymsg)
               self.round=0
            return response_message
        except Exception as e:
            print(e)
            return e


def get_contract_info(exchange_code, clearing_code, contract_code,product_type):

    conn = pyodbc.connect('DRIVER={SQL Server};SERVER=192.168.200.57;DATABASE=CMEClearDB;UID=sa;PWD=123456')
    
    # 构建查询语句
    query = f"SELECT top 10 * FROM TContract WHERE MQMExchangeCode like '%{exchange_code}%' AND ClearProductCode like '%{clearing_code}%' AND MMY like '%{contract_code}%' AND MQMSecType like '%{product_type}%'"
    
    
    cursor = conn.cursor()
    cursor.execute(query)
    rows = cursor.fetchall()
    
    
    cursor.close()
    conn.close()
    
    # 将结果拼接成字符串格式再次发给LLM推理
    result_string = ""
    for row in rows:
        contract_info_string = f"交易所代码：{row[1]}，清算代码：{row[2]}，合约日期：{row[4]}，产品类型：{row[5]}，最后交易日： {str(row[6])}，看涨看跌：{row[8]}，行权价：{row[9]}\n"
        result_string += contract_info_string
    
    return result_string

def answer_question(question):
    index="faiss_index"
    query = question
    txts =embedding.get_documents(index,query)
    return txts

