
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
                    "pattern":"^(?:[0-9]{2})(0[1-9]|1[0-2])$",
                    "description": "这是合约日期，必填项。比如2405,表示2024年5月份的合约，如果是LME（伦敦金属交易），ContractDate参数输入3M"
                },
                "strikePrice": {
                    "type": "number",
                    "description": "行权价，如果 commodityType 是 O（期权合约），请提供strikePrice"
                },
                "putCall": {
                    "type": "string",
                    "enum": ["C", "P"],
                    "description": "看涨看跌，看涨用C表示，看跌用P表示，如果 commodityType 是 O（期权合约），请提供putCall"
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
}
    ,
        {
    "type": "function",
    "function": {
        "name": "business_question",
        "description": "回答公司产品问题、业务问题以及金融方面的常识性问题",
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
                    {"role": "system", "content": "你是上海直达软件公司训练的智能金融助手小达，你能够帮助客户查询合约信息以及回答公司相关产品和业务方面的问题"},
                    {"role":"system","content":"请用与提问相同的语种回答"},
                    {"role": "system", "content": "不要假设或猜测传入函数的参数值。如果用户的描述不明确，请要求用户提供必要信息"},
                    {"role": "system", "content": "当用户说你好时，你要告诉用户你是谁"}
               ]

ToolPrompt=f"根据知识库内容：[knowledge]，详细回答以下问题：[question]，请用与提问相同的语种回答。如果你觉得知识库内容信息不足以回答问题，请根据你已拥有的知识简明扼要地回答"

ONLINE_LLM_MODEL = {
    "AzureOpenAI": {
        "model_name": "gpt-4",
        "api_base_url": "https://zdai1.openai.azure.com/",
        "api_version":"2024-02-15-preview",
        "api_key": "66332ca65cac487e8d64e4d63309b8cd",
        "openai_proxy": "",
        "embedding":"text-embedding-3-large"
    },
    "ZHIPU":{
        "model_name": "glm-3-turbo",
        "api_base_url":"https://open.bigmodel.cn/api/paas/v4/",
        "api_key":"0b4045234105a0f658a24da0ba2b65c2.8pRUJKMUITyXdrym"
        }
}

SimilaritySearchCfg={
    "top_k":4,
    "fetch_k":20,
    "min_score":0.2,
    "mapping_min_score":0.3
    }
TextSplitterCfg={
    "chunksize":600,
    "overlap":20
    }

hostinfo={"hostname":"192.168.200.57","port":"8000"}

CompleteionsPara={"temperature":0.3,"max_tokens":500}
ChatRound=5
wordsnum=300
javaapi="http://192.168.200.10:16001/chatGPT/contractInfo"

contentFilterAnswer="对不起，关于仇恨、性、暴力和自残的相关内容我拒绝回答！"

inneralError="发生内部异常，请联系技术支持！"