
import imp
from openai import AzureOpenAI
import os
from tools import tools
import json
import pyodbc
import embedding

class Conversation:
    def __init__(self):
        os.environ["AZURE_OPENAI_API_KEY"] = 'd58136d46efe4cedb8e9c33d682d518f'
        os.environ["OPENAI_API_VERSION"] = "2024-02-15-preview"
        os.environ["AZURE_OPENAI_ENDPOINT"] = "https://zdopenai.openai.azure.com/"
        self.client = AzureOpenAI()
        self.tools=tools

    def ask(self, question):
        try:
            messages=[
                      {"role": "system", "content": "你是上海直达软件公司训练的一个礼貌、耐心、友好、专业的企业技术支持客服，能够为客户查询产品或合约信息。"},
                      {"role": "system", "content": "不要假设或猜测传入函数的参数值。如果用户的描述不明确，请要求用户提供必要信息。"},
                      {"role":"system","content":"Only use the functions you have been provided with"}
                     ]
            messages.append({"role": "user", "content": question})
            response = self.client.chat.completions.create(
                model="gpt-4",
                messages=messages,
                tools=self.tools,
                tool_choice="auto",
                temperature=0.5,
            )
            response_message = response.choices[0].message
            tool_calls = response_message.tool_calls
            if tool_calls:
                messages.append(response_message)
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
                        
                    messages.append(
                       {
                            "tool_call_id": tool_call.id,
                            "role": "tool",
                            "name": function_name,
                            "content": f"你是个礼貌且聪明的助理，可以根据给定文档回答问题。通过搜索文档：{function_response}，回答以下问题：{question}。如果你觉得提供内容信息不足以回答这个问题，可以根据你的经验来回答",
                            #"content": f"{function_response},以json格式输出",
                       }
                    )
                second_response = self.client.chat.completions.create(
                model="gpt-4",
                messages=messages,
                #response_format={ "type": "json_object" },
                temperature =0.5)
                response_message = second_response.choices[0].message
                #print("Bot：", response_message.content)
            else:
                pass
               #print("Bot：", response_message.content)
            messages.append({"role": "assistant", "content": response_message.content})
            return response_message
        except Exception as e:
            print(e)
            return e

        
def get_contract_info(exchange_code, clearing_code, contract_code,product_type):
    # 连接到 SQL Server 数据库
    conn = pyodbc.connect('DRIVER={SQL Server};SERVER=192.168.200.57;DATABASE=CMEClearDB;UID=sa;PWD=123456')
    
    # 构建查询语句
    query = f"SELECT top 10 * FROM TContract WHERE MQMExchangeCode like '%{exchange_code}%' AND ClearProductCode like '%{clearing_code}%' AND MMY like '%{contract_code}%' AND MQMSecType like '%{product_type}%'"
    
    # 返回合约信息
    # 执行查询并获取结果
    cursor = conn.cursor()
    cursor.execute(query)
    rows = cursor.fetchall()
    
    # 关闭游标和数据库连接
    cursor.close()
    conn.close()
    
    # 将结果拼接成字符串格式
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

