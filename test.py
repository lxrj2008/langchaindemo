# coding=gbk
from openai import OpenAI
import json
import os
import httpx
from openai import AzureOpenAI
import requests

os.environ["AZURE_OPENAI_KEY"] = 'd58136d46efe4cedb8e9c33d682d518f'#��д�Լ���Azure Api_key

client = AzureOpenAI(
  azure_endpoint = "https://zdopenai.openai.azure.com/", 
  api_key=os.getenv("AZURE_OPENAI_KEY"),  
  api_version="2024-02-15-preview"
)


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

def getcmeproducts(productcode):
    url = "http://example.com"
    params = {"��Ʒ����": productcode}
    response = requests.get(url, params=params)
    if response.status_code == 200:
        txt= '��Ҫ��ѯ�Ĳ�Ʒ�ǣ�{} '
        return txt.format(productcode)
    else:
        return {"error": "Failed to fetch data from custom API"}

tools = [
        {
            "type": "function",
            "function": {
                "name": "get_current_weather",
                "description": "��ȡָ���������������",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "location": {
                            "type": "string",
                            "description": "�ض��ĳ���, �����Ϻ�������������",
                        },
                        "unit": {"type": "string", "enum": ["���϶ȣ��棩", "���϶ȣ��H��"]},
                    },
                    "required": ["location"],
                },
            },
        },
        {
            "type": "function",
            "function": {
                "name": "getcmeproducts",
                "description": "���ݲ�Ʒ�����ȡ��Ʒ��Ϣ",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "productcode": {
                            "type": "string",
                            "description": "�ڻ���Ʒ���룬����21",
                        } 
                    },
                    "required": ["productcode"],
                },
            },
        }
    ]

def chat_loop():
    while True:
        user_input = input("You: ")
        messages = [{"role": "user", "content": user_input}]
        
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
                "getcmeproducts": getcmeproducts,
            }
            for tool_call in tool_calls:
                function_name = tool_call.function.name
                if function_name == "getcmeproducts":
                    function_to_call = available_functions[function_name]
                    function_args = json.loads(tool_call.function.arguments)
                    function_response = function_to_call(productcode=function_args.get("productcode"))
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
                        "content": function_response,
                   }
                )

            second_response = client.chat.completions.create(
                model="gpt-4",
                messages=messages,
            )
            
            response_message = second_response.choices[0].message
            print("Bot:", response_message.content)
        else:
            print("Bot:", response_message.content)

        ## Ask if the user wants to continue the conversation
        #user_continue = input("Press ESC to eixt ")
        #if user_continue.lower() != "esc":
        #    print("Goodbye!")
        #    break

# Start the chat loop
chat_loop()

