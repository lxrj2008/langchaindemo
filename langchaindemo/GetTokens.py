import tiktoken


## 使用`tiktoken.get_encoding()`按名称加载编码。第一次运行时，它将需要互联网连接进行下载。后续运行不需要互联网连接。
#encoding1 = tiktoken.get_encoding("cl100k_base")
## 使用`tiktoken.encoding_for_model()`函数可以自动加载给定模型名称的正确编码。
#encoding2 = tiktoken.encoding_for_model("gpt-3.5-turbo")
## encoding1和encoding2是等价的，因为gpt-3.5-turbo使用的编码名称是cl100k_base
#print(encoding1.encode("tiktoken is great!"))
#print(encoding2.encode("tiktoken is great!"))

# 初始化GPT-3的编码器
enc = tiktoken.get_encoding("cl100k_base")

# 工具描述
tools = [
    {
        "type": "function",
        "function": {
            "name": "Get_Contract_Information",
            "description": "查询合约数据。当用户提供了交易所代码、产品代码、合约日期和商品类型时，调用此工具获取合约信息。期权合约需要额外提供行权价和看涨看跌信息。",
            "parameters": {
                "type": "object",
                "properties": {
                    "ExchangeCode": {
                        "type": "string", 
                        "description": "交易所代码，必填项。例如：CME"
                    },
                    "ProductCode": {
                        "type": "string",
                        "description": "商品代码，必填项。例如：CL"
                    },
                    "commodityType": {
                        "type": "string",
                        "enum": ["F", "O"],
                        "description": "商品类型，必填项。期货用F表示，期权用O表示"
                    },
                    "ContractDate": {
                        "type": "string",
                        "pattern":"^(?:[0-9]{2})(0[1-9]|1[0-2])$",
                        "description": "合约日期，必填项。例如：2405表示2024年5月份的合约，LME（伦敦金属交易）使用3M表示"
                    },
                    "strikePrice": {
                        "type": "number",
                        "description": "行权价，如果是期权合约，请提供行权价"
                    },
                    "putCall": {
                        "type": "string",
                        "enum": ["C", "P"],
                        "description": "看涨看跌，如果是期权合约，请提供。看涨用C表示，看跌用P表示"
                    }
                },
                "required": ["ExchangeCode", "commodityType","ProductCode", "ContractDate"],
                "if": {
                    "properties": {
                        "commodityType": { "const": "O" }
                    }
                },
                "then": {
                    "required": ["putCall","strikePrice"]
                }
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "business_question",
            "description": "查询业务问题。适用于用户提出开户、出入金、账户、交易、保证金、合约、行情、权限、费用、换汇、风控等相关问题。",
            "parameters": {
                "type": "object",
                "properties": {
                    "question": {
                        "type": "string",
                        "description": "用户提出的问题。例如：开户需要提前准备什么资料"
                    }
                },
                "required": ["question"]
            }
        }
    }
]

# 系统提示词
SystemPrompt = [
    {"role": "system", "content": "你是上海直达软件公司训练的智能助手小达，你能够帮助客户查询合约信息以及回答公司相关产品和业务方面的问题。"},
    {"role": "system", "content": "不要假设或猜测传入函数的参数值。如果用户的描述不明确，请要求用户提供必要信息。"},
    {"role": "system", "content": "当用户向你问好时，请告诉他们你是上海直达软件公司训练的智能助手小达。"},
    {"role": "system", "content": "对于常见的通用知识问题，请直接回答。如果问题涉及合约信息或特定的业务问题，请根据需要调用相应的工具。"}
]

# 工具提示词
ToolPrompt = "根据以下内容：[knowledge]，详细回答以下问题：[question]。请用与提问相同的语言回答。如果你认为[knowledge]中的信息不足以回答问题，请回答'不知道'，并表明你的专长。"

# 计算 tokens 数量
tools_tokens = sum([len(enc.encode(str(tool))) for tool in tools])
system_prompt_tokens = sum([len(enc.encode(prompt["content"])) for prompt in SystemPrompt])
tool_prompt_tokens = len(enc.encode(ToolPrompt))

# 输出结果
print(tools_tokens, system_prompt_tokens, tool_prompt_tokens, tools_tokens + system_prompt_tokens + tool_prompt_tokens)
