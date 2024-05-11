
from openai import AzureOpenAI
import os,json,pyodbc,copy
import cfg,embedding
from collections import deque
from mylogging import setup_logging
import requests

os.environ["AZURE_OPENAI_API_KEY"] = cfg.ONLINE_LLM_MODEL["AzureOpenAI"]["api_key"]
os.environ["OPENAI_API_VERSION"] = cfg.ONLINE_LLM_MODEL["AzureOpenAI"]["api_version"]
os.environ["AZURE_OPENAI_ENDPOINT"] = cfg.ONLINE_LLM_MODEL["AzureOpenAI"]["api_base_url"]

logger_info, logger_error,logger_debug = setup_logging()

client = AzureOpenAI()

class ErrorMessage:
    def __init__(self, content):
        self.content = content

class Conversation:
    
    def __init__(self,username=None):
        self.username=username
        self.tools=cfg.tools
        self.messages = deque(copy.deepcopy(cfg.SystemPrompt))#first in first out queue
        self.round=0;

    def ask(self,question):
        try:
            self.messages.append({"role": "user", "content": question})
            logger_info.info(f"{self.username} ask:{question}")
            logger_debug.info(f"{self.username}:{self.messages}");
            response = client.chat.completions.create(
                model=cfg.ONLINE_LLM_MODEL["AzureOpenAI"]["model_name"],
                messages=self.messages,
                tools=self.tools,
                tool_choice="auto",
                temperature=cfg.CompleteionsPara["temperature"],
                max_tokens=cfg.CompleteionsPara["max_tokens"]
            )
            logger_debug.info(f'{self.username} first token：{str(response.usage)}')
            logger_debug.info(f'{self.username} first prompt filter：{str(response.prompt_filter_results)}')
            response_message = response.choices[0].message
            tool_calls = response_message.tool_calls
            if tool_calls:
                self.messages.append(response_message)
                for tool_call in tool_calls:
                    function_name = tool_call.function.name
                    function_result = {}
                    args = tool_call.function.arguments
                    if function_name == "Get_Contract_Information":
                        logger_debug.info(f"{self.username}:functionName:{function_name},args:{args}");
                        function_response = Get_Contract_Information(**json.loads(args))
                    
                    elif function_name=="answer_other_question" :
                        logger_debug.info(f"{self.username}:functionName:{function_name},args:{args}");
                        function_response=answer_other_question(**json.loads(args))
                    else:
                        logger_debug.info(f"{self.username}:no function selected,but default functionName:{function_name},args:{args}");
                        function_response = answer_other_question(**json.loads(args))
                        
                    self.messages.append(
                       {
                            "tool_call_id": tool_call.id,
                            "role": "tool",
                            "name": function_name,
                            "content": cfg.ToolPrompt.replace("knowledge", function_response).replace("question", question)
                            #"content": f"{function_response},以json格式输出",
                       }
                    )
                second_response = client.chat.completions.create(
                model=cfg.ONLINE_LLM_MODEL["AzureOpenAI"]["model_name"],
                messages=self.messages,
                #response_format={ "type": "json_object" },
                temperature=cfg.CompleteionsPara["temperature"],
                max_tokens=cfg.CompleteionsPara["max_tokens"])
                logger_debug.info(f'{self.username} second token：{str(second_response.usage)}')
                logger_debug.info(f'{self.username} second prompt filter：{str(second_response.prompt_filter_results)}')
                response_message = second_response.choices[0].message
            else:
                logger_debug.info(f'{self.username}:no tools is called')
            self.messages.append({"role": "assistant", "content": response_message.content})
            self.round += 1
            if self.round >= cfg.ChatRound:
               logger_debug.info(f"{self.username}:ChatRound:{self.round}");
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
            logger_info.info(f"{self.username} answer:{response_message.content}");   
            logger_debug.info(f"{self.username}:{self.messages}");
            return response_message
        except Exception as e:
            
            logger_error.error(f"{self.username}：An error occurred: %s", e)
            if e.status_code==400 and e.code=='content_filter':
                response_message = ErrorMessage(cfg.contentFilterAnswer)
            else:
                response_message=ErrorMessage(cfg.inneralError)
            logger_info.info(f"{self.username} answer:{response_message.content}"); 
            return response_message
            
def Get_Contract_Information(ExchangeCode,ProductCode,ContractDate,commodityType,strikePrice=None,putCall=None):
    try:
        data = {"exchange": ExchangeCode, "commodity": ProductCode, "contract": ContractDate,"commodityType":commodityType}
        if commodityType.upper()=="O":
            ProductCode=ProductCode+"_"+putCall
            data = {"exchange": ExchangeCode, "commodity": ProductCode, "contract": ContractDate,"commodityType":commodityType}
        json_data = json.dumps(data, ensure_ascii=False).encode('utf-8')
        headers = {'Content-Type': 'application/json; charset=utf-8'}
        response = requests.request("POST", cfg.javaapi, headers=headers, data=json_data)
        response.encoding = 'utf-8'
        if response.status_code == 200:
            content=response.json()["data"]
            if(len(content)>0):
                contract_info_string=''
                num=1;
                for item in content:
                    contract_info_string += (
                                            f"第{num}个合约\n"
                                            f"合约代码：{item['contractCode']}\n"
                                            f"中文名：{item['contractName']}\n"
                                            f"英文名：{item['contractNameEn']}\n"
                                            f"合约号：{item['contractNo']}\n"
                                            f"商品代码：{item['commodityNo']}\n"
                                            f"商品中文名：{item['commodityName']}\n"
                                            f"商品英文名：{item['commodityNameEn']}\n"
                                            f"商品币种：{item['commodityCurrencyNo']}\n"
                                            f"币种名字：{item['commodityCurrencyName']}\n"
                                            f"商品类型：{item['commodityType']}\n"
                                            f"交易所代码：{item['exchangeNo']}\n"
                                            f"交易所名称：{item['exchangeName']}\n"
                                            f"账面跳点：{item['productDot']}\n"
                                            f"最小变动单位：{item['upperTick']}\n"
                                            f"进价单位：{item['lowerTick']}\n"
                                            f"行情小数点位数：{item['dotNum']}\n"
                                            f"首次通知日：{item['firstNoticeDay']}\n"
                                            f"合约到期日：{item['expiryDate']}\n"
                                            f"最后交易日：{item['lastTradeDate']}\n\n"
                                            )   
                    num += 1
                    if num>5:
                        break
                return contract_info_string
            else:
                return '未查询到您要的合约数据'
        else:
            logger_error.error(f"request java api fial:{response.status_code}")
            return None
    except Exception as e:
        logger_error.error(f"Get_Contract_Information error:{str(e)}")
        return None

def answer_other_question(question):
    index="faiss_index"
    query = question
    txts =embedding.get_documents(index,query)
    return txts



