
tools = [
        {
    "type": "function",
    "function": {
        "name": "Get_Contract_Information",
        "description": "根据交易所代码、产品代码、合约日期、商品类型等信息查询对应的合约数据",
        "parameters": {
            "type": "object",
            "properties": {
                "ExchangeCode": {
                    "type": "string", 
                    "description": "这是交易所代码，必填项"
                },
                "ProductCode": {
                    "type": "string",
                    "description": "这是商品代码，必填项"
                },
                "commodityType": {
                    "type": "string",
                    "enum": ["F", "O"],
                    "description": "这是商品类型,必填项。期货合约是用F表示，期权合约是用O表示"
                },
                "ContractDate": {
                    "type": "string",
                    "pattern":"^\\d{4}$",
                    "description": "这是合约日期，必填项。比如2405,表示2024年5月份的合约，如果是LME（伦敦金属交易），ContractDate参数输入3M"
                },
                "strikePrice": {
                    "type": "number",
                    "description": "行权价，如果 commodityType 是 O（期权合约），因为期权合约的不同行权价会非常多，请提供strikePrice进行过滤，不提供也可以，但可能会查询出很多记录"
                },
                "putCall": {
                    "type": "string",
                    "enum": ["C", "P"],
                    "description": "看涨看跌，看涨用C表示，看跌用P表示，如果 commodityType 是 O（期权合约），请提供putCall，不提供也可以，但可能会查询出很多记录"
                }

            },
            "required": ["ExchangeCode", "commodityType","ProductCode", "ContractDate"],
            #"if": {
            #    "properties": {
            #      "commodityType": { "const": "O" }
            #      }
            #    },
            #  "then": {
            #    "required": ["putCall"]
            #  }

        }
    }
}
    ,
        {
    "type": "function",
    "function": {
        "name": "answer_other_question",
        "description": "回答工具{Get_Contract_Information}以外的其他问题。",
        "parameters": {
            "type": "object",
            "properties": {
                "question": {
                    "type": "string",
                    "description": "用户提出的问题"
                }
            },
            "required": ["question"]
        }
    }
}]

SystemPrompt = [
                    {"role": "system", "content": "你是上海直达软件公司训练的智能查询助手小达达，你能够帮助客户查询合约信息以及回答公司相关产品和业务方面的问题"},
                    {"role": "system", "content": "不要对要插入函数的值进行假设，如果用户请求不明确，请要求用户澄清"},
                    {"role": "system", "content": "当用户说你好时，你要告诉用户你是谁"},
                    {"role":"system","content":"只使用提供给你的函数"}
               ]

ToolPrompt=f"根据知识库内容：[knowledge]，回答以下问题：[question]。如果你觉得知识库内容信息不足以回答这个问题，请回答不知道并且表明你的专长或者根据你已拥有的知识来回答"

ONLINE_LLM_MODEL = {
    "AzureOpenAI": {
        "model_name": "gpt-4",
        "api_base_url": "https://zdai1.openai.azure.com/",
        "api_version":"2024-02-15-preview",
        "api_key": "66332ca65cac487e8d64e4d63309b8cd",
        "openai_proxy": "",
        "embedding":"text-embedding-3-large"
    },
}

SimilaritySearchCfg={
    "top_k":4,
    "fetch_k":20,
    "min_score":0.2,
    "mapping_min_score":0.3
    }
TextSplitterCfg={
    "chunksize":250,
    "overlap":50
    }

hostinfo={"hostname":"192.168.200.57","port":"8001"}

CompleteionsPara={"temperature":0,"max_tokens":1000}
ChatRound=5
wordsnum=300
javaapi="http://192.168.200.28:16001/chatGPT/contractInfo"

contentFilterAnswer="对不起，关于仇恨、性、暴力和自残的相关内容我拒绝回答！"

inneralError="发生内部异常，请联系技术支持！"