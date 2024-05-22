
from openai import AzureOpenAI
import os,json,copy
import cfg,embedding
from collections import deque
from mylogging import setup_logging
import requests
import random

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
            button=''
            self.messages.append({"role": "user", "content": question})
            logger_info.info(f"{self.username} ask:{question}")
            logger_debug.info(f"{self.username}:{self.messages}");
            response = client.chat.completions.create(
                model=cfg.ONLINE_LLM_MODEL["AzureOpenAI"]["model_name"],
                messages=self.messages,
                tools=self.tools,
                tool_choice="auto",
                n=1,
                max_tokens=cfg.CompleteionsPara["max_tokens"],
                temperature=cfg.CompleteionsPara["temperature"]
            )
            logger_debug.info(f'{self.username} first token：{str(response.usage)}')
            logger_debug.info(f'{self.username} first prompt filter：{str(response.prompt_filter_results)}')
            response_message = response.choices[0].message
            tool_calls = response_message.tool_calls
            if tool_calls:
                self.messages.append(response_message)
                for tool_call in tool_calls:
                    function_name = tool_call.function.name
                    args = tool_call.function.arguments
                    if function_name == "Get_Contract_Information":
                        logger_debug.info(f"{self.username}:functionName:{function_name},args:{args}");
                        function_response = Get_Contract_Information(**json.loads(args))
                    
                    elif function_name=="business_question" :
                        logger_debug.info(f"{self.username}:functionName:{function_name},args:{args}");
                        function_response=business_question(**json.loads(args))
                    else:
                        logger_debug.info(f"{self.username}:no function selected,but default functionName:{function_name},args:{args}");
                        function_response = business_question(**json.loads(args))
                        
                    self.messages.append(
                       {
                            "tool_call_id": tool_call.id,
                            "role": "tool",
                            "name": function_name,
                            "content": cfg.ToolPrompt.replace("knowledge", function_response["content"]).replace("question", question)
                            #"content": f"{function_response},以json格式输出",
                       }
                    )

                second_response = client.chat.completions.create(
                model=cfg.ONLINE_LLM_MODEL["AzureOpenAI"]["model_name"],
                messages=self.messages,
                #response_format={ "type": "json_object" },
                n=1,
                temperature=cfg.CompleteionsPara["temperature"],
                max_tokens=cfg.CompleteionsPara["max_tokens"])
                logger_debug.info(f'{self.username} second token：{str(second_response.usage)}')
                logger_debug.info(f'{self.username} second prompt filter：{str(second_response.prompt_filter_results)}')
                response_message = second_response.choices[0].message
                if function_response:
                    button=function_response["button"]
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
            logger_debug.info(f"{self.username}:{self.messages}");
        except Exception as e:
            
            logger_error.error(f"{self.username}：An error occurred: %s", e)
            if e.status_code==400 and e.code=='content_filter':
                random_answer = random.choice(cfg.contentFilterAnswer)
                response_message = ErrorMessage(random_answer)
            elif e.status_code==400 and e.code=='context_length_exceeded':
                self.messages=deque(copy.deepcopy(cfg.SystemPrompt))
                self.round=0
                response_message = ErrorMessage("本轮会话tokens已超上限，已帮您重置，请继续提问吧！")
            else:
                response_message=ErrorMessage(cfg.inneralError)
        logger_info.info(f"{self.username} answer:{response_message.content}"); 
        responsecontent={"answer":f"{response_message.content}","button":f"{button}"}
        return responsecontent
            
def Get_Contract_Information(ExchangeCode,ProductCode,ContractDate,commodityType,strikePrice=None,putCall=None):
    try:
        content=''
        button=''
        logger_debug.info(f"原始的ExchangeCode：{ExchangeCode}")
        logger_debug.info(f"原始的ProductCode：{ProductCode}")
        ExchangeCode=embedding.get_mapping_documents("mapping_faiss",ExchangeCode,cfg.SimilaritySearchCfg["mapping_min_score"])
        ProductCode=embedding.get_mapping_documents("mapping_faiss",ProductCode,cfg.SimilaritySearchCfg["mapping_min_score"])
        logger_debug.info(f"Mapping后的ExchangeCode：{ExchangeCode}")
        logger_debug.info(f"Mapping后的ProductCode：{ProductCode}")
        if commodityType.upper()=="O" and putCall:
            ProductCode=ProductCode+"_"+putCall
        data = {"exchange": ExchangeCode, "commodity": ProductCode, "contract": ContractDate,"commodityType":commodityType,"strikePrice":strikePrice}
        json_data = json.dumps(data, ensure_ascii=False).encode('utf-8')
        headers = {'Content-Type': 'application/json; charset=utf-8'}
        response = requests.request("POST", cfg.javaapi, headers=headers, data=json_data)
        response.encoding = 'utf-8'
        if response.status_code == 200:
            datacontent=response.json()["data"]
            if(len(datacontent)>0):
                contract_info_string=''
                num=1;
                for item in datacontent:
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
                                            f"最后交易日：{item['lastTradeDate']}\n"
                                            f"行权价：{item['strikePrice']}\n"
                                            f"保证金：{item['defaultDeposit']}\n"
                                            f"手续费：{item['defaultFee']}\n"
                                            )   
                    num += 1
                    if num>3:
                        break
                content=contract_info_string
            else:
                content= '未查询到您要的合约数据,请确认查询条件是否正确'
        else:
            logger_error.error(f"request java api fial:{response.status_code}")
    except Exception as e:
        logger_error.error(f"Get_Contract_Information error:{str(e)}")
    data={"content":f"{content}","button":f"{button}"}
    return data

def business_question(question):
    index="faiss_index"
    query = question
    txts =embedding.get_documents(index,query,cfg.SimilaritySearchCfg["min_score"])
    return txts



