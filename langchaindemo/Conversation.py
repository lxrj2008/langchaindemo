
from openai import AzureOpenAI
import os,json,pyodbc,copy
import cfg,embedding

os.environ["AZURE_OPENAI_API_KEY"] = cfg.ONLINE_LLM_MODEL["AzureOpenAI"]["api_key"]
os.environ["OPENAI_API_VERSION"] = cfg.ONLINE_LLM_MODEL["AzureOpenAI"]["api_version"]
os.environ["AZURE_OPENAI_ENDPOINT"] = cfg.ONLINE_LLM_MODEL["AzureOpenAI"]["api_base_url"]

class Conversation:
    def __init__(self,username=None):
        self.client = AzureOpenAI()
        self.username=username
        self.tools=cfg.tools
        self.messages = copy.deepcopy(cfg.SystemPrompt)
        

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
                            "content": f"你是上海直达软件有限公司开发的智能机器人小达达，你非常专业，可以根据上下文回答问题。请根据上下文：{function_response}，回答以下问题：{question}。如果你觉得上下文内容信息不足以回答这个问题，你可以回复不知道或者根据你的经验来回答",
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
    txts =embedding.get_documents(index,query,3)
    return txts

