# coding=gbk
import imp
from openai import AzureOpenAI
import os
from tools import tools
import json
import pyodbc

class Conversation:
    def __init__(self, prompt):
        os.environ["AZURE_OPENAI_KEY"] = 'd58136d46efe4cedb8e9c33d682d518f'

        self.client = AzureOpenAI(
        azure_endpoint = "https://zdopenai.openai.azure.com/", 
        api_key=os.getenv("AZURE_OPENAI_KEY"),  
        api_version="2024-02-15-preview")
        self.prompt = prompt
        self.messages = []
        self.messages.append({"role": "system", "content": self.prompt})
        self.tools=tools

    def ask(self, question):
        try:
            messages=[{"role": "system", "content": "�����Ϻ�ֱ�������˾ѵ����һ�����ġ��Ѻá�רҵ����ҵ����֧�ֿͷ����ܹ�Ϊ�ͻ���ѯ�ض��Ĳ�Ʒ���Լ��Ϣ.�����Ľ�����"}]
            messages.append({"role": "user", "content": question})
            #self.messages.append({"role": "user", "content": question})
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
                #self.messages.append(response_message)
                messages.append(response_message)
                available_functions = {
                "get_current_weather": get_current_weather,
                "get_contract_info": get_contract_info,}
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
                    #self.messages.append(
                    #   {
                    #       "tool_call_id": tool_call.id,
                    #        "role": "tool",
                    #        "name": function_name,
                    #        "content": f"{function_response},��json��ʽ���",
                    #   }
                    #)
                    messages.append(
                       {
                           "tool_call_id": tool_call.id,
                            "role": "tool",
                            "name": function_name,
                            "content": f"{function_response},��json��ʽ���",
                       }
                    )
                second_response = self.client.chat.completions.create(
                model="gpt-4",
                messages=messages,
                response_format={ "type": "json_object" },
                temperature =0.5)
                response_message = second_response.choices[0].message
                print("Bot:", response_message.content)
            else:
               print("Bot:", response_message.content)
            #self.messages.append({"role": "assistant", "content": response_message.content})
            messages.append({"role": "assistant", "content": response_message.content})
            #if len(self.messages) > self.num_of_round*2 + 1:
            #del self.messages[1:3] #Remove the first round conversation left.
            return response_message
        except Exception as e:
            print(e)
            return e

        

def get_current_weather(location, unit="���϶ȣ��棩"):
    """��ȡ����λ�õ��������"""
    if "�Ϻ�" in location.lower():
        return json.dumps({"location": "�Ϻ�", "temperature": "10", "unit": unit})
    elif "����" in location.lower():
        return json.dumps({"location": "����", "temperature": "15", "unit": unit})
    elif "����" in location.lower():
        return json.dumps({"location": "����", "temperature": "17", "unit": unit})
    else:
        return json.dumps({"location": location, "temperature": "unknown"})

def get_contract_info(exchange_code, clearing_code, contract_code):
    # ���ӵ� SQL Server ���ݿ�
    conn = pyodbc.connect('DRIVER={SQL Server};SERVER=192.168.200.57;DATABASE=CMEClearDB;UID=sa;PWD=123456')
    
    # ������ѯ���
    query = f"SELECT * FROM TContract WHERE MQMExchangeCode like '%{exchange_code}%' AND ClearProductCode like '%{clearing_code}%' AND MMY like '%{contract_code}%'"
    
    # ���غ�Լ��Ϣ
    # ִ�в�ѯ����ȡ���
    cursor = conn.cursor()
    cursor.execute(query)
    rows = cursor.fetchall()
    
    # �ر��α�����ݿ�����
    cursor.close()
    conn.close()
    
    # �����ƴ�ӳ��ַ�����ʽ
    result_string = ""
    for row in rows:
        contract_info_string = f"���������룺{row[1]}��������룺{row[2]}����Լ���ڣ�{row[4]}����Ʒ���ͣ�{row[5]}��������գ� {str(row[6])}�����ǿ�����{row[8]}����Ȩ�ۣ�{row[9]}\n"
        result_string += contract_info_string
    
    return result_string
