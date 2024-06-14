from openai import AzureOpenAI
import os, json, copy
import cfg, embedding
from collections import deque
from mylogging import setup_logging
import requests
import random
from datetime import datetime, timedelta
import time

def setup_environment():
    os.environ["AZURE_OPENAI_API_KEY"] = cfg.ONLINE_LLM_MODEL["AzureOpenAI"]["api_key"]
    os.environ["OPENAI_API_VERSION"] = cfg.ONLINE_LLM_MODEL["AzureOpenAI"]["api_version"]
    os.environ["AZURE_OPENAI_ENDPOINT"] = cfg.ONLINE_LLM_MODEL["AzureOpenAI"]["api_base_url"]

def get_logger():
    logger_info, logger_error, logger_debug = setup_logging()
    return logger_info, logger_error, logger_debug

setup_environment()
logger_info, logger_error, logger_debug = get_logger()
client = AzureOpenAI()
tools = cfg.tools

class ErrorMessage:
    def __init__(self, content):
        self.content = content

class Conversation:
    def __init__(self, username=None):
        self.username = username
        self.messages = deque(copy.deepcopy(cfg.fixed_SystemPrompt))
        self.last_request_time = datetime.now()
    def ask(self, question):
        try:
            current_time = datetime.now()
            if current_time - self.last_request_time > timedelta(hours=cfg.reset_session_interval):
                self.messages = deque(copy.deepcopy(cfg.fixed_SystemPrompt))
                logger_debug.info(f"{self.username}: reset session")
            self.last_request_time = current_time
            chat_round = sum(1 for msg in self.messages if isinstance(msg, dict) and msg.get("role") == "user")
            if chat_round>=cfg.ChatRound:
                self.handle_message_queue()
            button = ''
            self.messages.append({"role": "user", "content": question})
            logger_info.info(f"{self.username} ask: {question}")
            logger_debug.info(f"{self.username}: {self.messages}")
            response = self.get_response_from_model(IsTool=True)
            logger_debug.info(f'{self.username} first token: {str(response.usage)}')
            logger_debug.info(f'{self.username} first prompt filter: {str(response.prompt_filter_results)}')
            response_message = response.choices[0].message
            tool_calls = response_message.tool_calls
            if tool_calls:
                self.messages.append(response_message)
                function_response=self.handle_tool_calls(tool_calls, question)
                second_response = self.get_response_from_model()
                logger_debug.info(f'{self.username} second token: {str(second_response.usage)}')
                logger_debug.info(f'{self.username} second prompt filter: {str(second_response.prompt_filter_results)}')
                response_message = second_response.choices[0].message
                if function_response:
                    button = function_response["button"]
            else:
                logger_debug.info(f'{self.username}: no tools called')

            self.messages.append({"role": "assistant", "content": response_message.content})
            logger_debug.info(f"{self.username}: {self.messages}")

        except Exception as e:
            logger_error.error(f"{self.username}: An error occurred: {e}")
            if e.status_code==400 and e.code=='content_filter':
                random_answer = random.choice(cfg.contentFilterAnswer)
                response_message = ErrorMessage(random_answer)
                self.messages.pop()
            elif e.status_code==400 and e.code=='context_length_exceeded':
                self.messages = deque(copy.deepcopy(cfg.fixed_SystemPrompt))
                response_message = ErrorMessage("超过令牌限制，会话重置。请继续提问!")
            else:
                response_message=ErrorMessage(cfg.inneralError)

        logger_info.info(f"{self.username} answer: {response_message.content}")
        return {"answer": response_message.content, "button": button}

    def get_response_from_model(self, IsTool=None):
        params = {
            "model": cfg.ONLINE_LLM_MODEL["AzureOpenAI"]["model_name"],
            "messages": self.messages,
            #response_format={ "type": "json_object" },
            "n": 1,
            "max_tokens": cfg.CompleteionsPara["max_tokens"],
            "temperature": cfg.CompleteionsPara["temperature"]
        }
        if IsTool:
            params.update({
                "tools": tools,
                "tool_choice": "auto"
            })

        return client.chat.completions.create(**params)


    def handle_tool_calls(self, tool_calls, question):
        
        for tool_call in tool_calls:
            function_name = tool_call.function.name
            args = json.loads(tool_call.function.arguments)
            if function_name == "Get_Contract_Information":
                logger_debug.info(f"{self.username}:functionName:{function_name},args:{args}");
                function_response=self.Get_Contract_Information(**args)
            elif function_name == "any_other_questions":
                logger_debug.info(f"{self.username}:functionName:{function_name},args:{args}");
                function_response=self.any_other_questions(**args)
            else:
                logger_debug.info(f"{self.username}:no function selected,but default functionName:{function_name},args:{args}");
                function_response=self.any_other_questions(**args)
            self.messages.append(
                {
                    "tool_call_id": tool_call.id,
                    "role": "tool",
                    "name": function_name,
                    #"content": f"{function_response},以json格式输出",
                    "content": cfg.ToolPrompt.replace("knowledge", function_response["content"]).replace("question", question)
                }
            )
        return function_response

    def handle_message_queue(self):
        # 弹出前三个元素并保存
        first_three_messages = [self.messages.popleft() for _ in range(len(cfg.fixed_SystemPrompt))]
        user_count = 0
        while self.messages:
            #弹出
            msg = self.messages.popleft()
            if isinstance(msg, dict) and msg.get("role") == "user":
                user_count += 1
            if user_count == 2:
                self.messages.appendleft(msg)
                break
        # 将前三个元素放回队列，并且位置不变
        for mymsg in reversed(first_three_messages):
            self.messages.appendleft(mymsg)
            

    def Get_Contract_Information(self, ExchangeCode, ProductCode, ContractNo, commodityType, strikePrice=None, putCall=None):
        try:
            content, button = '', ''
            logger_debug.info(f"Original ExchangeCode: {ExchangeCode}")
            logger_debug.info(f"Original ProductCode: {ProductCode}")
            
            ExchangeCode = embedding.get_mapping_documents("mapping_faiss", ExchangeCode, cfg.SimilaritySearchCfg["mapping_min_score"])
            ProductCode = embedding.get_mapping_documents("mapping_faiss", ProductCode, cfg.SimilaritySearchCfg["mapping_min_score"])

            logger_debug.info(f"Mapped ExchangeCode: {ExchangeCode}")
            logger_debug.info(f"Mapped ProductCode: {ProductCode}")

            if commodityType.upper() == "O" and putCall:
                pass
                #ProductCode += f"_{putCall}"
            start_time = time.time()
            data = {"exchange": ExchangeCode, "commodity": ProductCode, "contract": ContractNo, "commodityType": commodityType, "strikePrice": strikePrice}
            logger_debug.info(f"{self.username} pass pram:{data}")
            response = requests.post(cfg.javaapi, headers={'Content-Type': 'application/json; charset=utf-8'}, json=data)
            response.encoding = 'utf-8'

            if response.status_code == 200:
                datacontent = response.json().get("data", [])
                if datacontent and commodityType.upper()=='F':
                   datacontent=self.filter_contracts(datacontent, ExchangeCode, ProductCode)
                if datacontent:
                    content = self.format_contract_info(datacontent)
                else:
                    content = '未查询到您要的合约数据,请确认查询条件是否正确.'
                    logger_debug.info(f"{self.username}，{content}")
            else:
                logger_error.error(f"Failed to request Java API: {response.status_code}")
            end_time = time.time()
            elapsed_time = end_time - start_time  
            logger_debug.info(f'call contractInfo api take time：{elapsed_time}秒')

        except Exception as e:
            logger_error.error(f"Get_Contract_Information error: {str(e)}")

        return {"content": content, "button": button}

    def filter_contracts(self,contracts, exchange_no, commodity_no):
        return list(filter(lambda x: x['exchangeNo'] == exchange_no and x['commodityNo'] == commodity_no, contracts))

    def format_contract_info(self, datacontent):
        contract_info_string = ''
        for num, item in enumerate(datacontent[:3], start=1):
            contract_info_string += (
                f"第{num}个合约\n"
                f"合约代码：{item['contractCode']}\n"
                f"合约名称：{item['contractName']}\n"
                f"商品代码：{item['commodityNo']}\n"
                f"商品名称：{item['commodityName']}\n"
                f"币种：{item['commodityCurrencyNo']}\n"
                f"商品类型：{item['commodityType']}\n"
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
        return contract_info_string

    def any_other_questions(self, question):
        index = "faiss_index"
        txts = embedding.get_documents(index, question, cfg.SimilaritySearchCfg["min_score"])
        return txts
