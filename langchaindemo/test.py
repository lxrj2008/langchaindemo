# coding=gbk
from openai import OpenAI
import json
import os
import httpx
from openai import AzureOpenAI
import requests
import pyodbc


os.environ["AZURE_OPENAI_KEY"] = 'd58136d46efe4cedb8e9c33d682d518f'#填写自己的Azure Api_key

client = AzureOpenAI(
  azure_endpoint = "https://zdopenai.openai.azure.com/", 
  api_key=os.getenv("AZURE_OPENAI_KEY"),  
  api_version="2024-02-15-preview"
)


def get_current_weather(location, unit="摄氏度（℃）"):
    """获取给定位置的天气情况"""
    if "上海" in location.lower():
        return json.dumps({"location": "上海", "temperature": "10", "unit": unit})
    elif "北京" in location.lower():
        return json.dumps({"location": "北京", "temperature": "15", "unit": unit})
    elif "广州" in location.lower():
        return json.dumps({"location": "广州", "temperature": "17", "unit": unit})
    else:
        return json.dumps({"location": location, "temperature": "unknown"})

def get_contract_info(exchange_code, clearing_code, contract_code):
    # 连接到 SQL Server 数据库
    conn = pyodbc.connect('DRIVER={SQL Server};SERVER=192.168.200.57;DATABASE=CMEClearDB;UID=sa;PWD=123456')
    
    # 构建查询语句
    query = f"SELECT * FROM TContract WHERE MQMExchangeCode like '%{exchange_code}%' AND ClearProductCode like '%{clearing_code}%' AND MMY like '%{contract_code}%'"
    
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

tools = [
        {
            "type": "function",
            "function": {
                "name": "get_current_weather",
                "description": "获取指定地区的天气情况",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "location": {
                            "type": "string",
                            "description": "特定的城市, 比如上海、北京、广州",
                        },
                        "unit": {"type": "string", "enum": ["摄氏度（℃）", "华氏度（℉）"]},
                    },
                    "required": ["location"],
                },
            },
        },
        {
    "type": "function",
    "function": {
        "name": "get_contract_info",
        "description": "你是一个专业的合约、产品查助手，能够为客户查询特定的产品或合约信息",
        "parameters": {
            "type": "object",
            "properties": {
                "exchange_code": {
                    "type": "string",
                    "description": "交易所代码,比如CME"
                },
                "clearing_code": {
                    "type": "string",
                    "description": "清算代码，比如MNQ"
                },
                "contract_code": {
                    "type": "string",
                    "description": "合约日期，比如20230900"
                }
            },
            "required": ["exchange_code", "clearing_code", "contract_code"]
        }
    }
}

    ]

def chat_loop():
    while True:
        messages=[{"role": "system", "content": "你是上海直达软件公司训练的一个耐心、友好、专业的企业技术支持客服，能够为客户查询特定的产品或合约信息.用中文交流！"}]
        
        user_input = input("You: ")
        inputstr = {"role": "user", "content": f"{user_input}"}
        messages.append(inputstr);
        
        response = client.chat.completions.create(
            model="gpt-4",
            messages=messages,
            tools=tools,
            tool_choice="auto",
        )
        
        response_message = response.choices[0].message
        tool_calls = response_message.tool_calls
        
        if tool_calls:
            messages.append(response_message)
            available_functions = {
                "get_current_weather": get_current_weather,
                "get_contract_info": get_contract_info,
            }
            for tool_call in tool_calls:
                function_name = tool_call.function.name
                if function_name == "get_contract_info":
                    function_to_call = available_functions[function_name]
                    function_args = json.loads(tool_call.function.arguments)
                    function_response = function_to_call(exchange_code=function_args.get("exchange_code"),clearing_code=function_args.get("clearing_code"),contract_code=function_args.get("contract_code"))
                else:
                    function_to_call = available_functions[function_name]
                    function_args = json.loads(tool_call.function.arguments)
                    function_response = function_to_call(
                        location=function_args.get("location"),
                        unit=function_args.get("unit"),
                    )
                messages.append(
                   {
                       "tool_call_id": tool_call.id,
                        "role": "tool",
                        "name": function_name,
                        "content": f"{function_response},以json格式输出",
                   }
                )

            second_response = client.chat.completions.create(
                model="gpt-4",
                messages=messages,
                response_format={ "type": "json_object" },
            )
            
            response_message = second_response.choices[0].message
            print("Bot:", response_message.content)
        else:
            print("Bot:", response_message.content)

# Start the chat loop
chat_loop()

