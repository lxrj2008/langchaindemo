

tools = [
        {
    "type": "function",
    "function": {
        "name": "Get_Contract_Information",
        "description": "查询合约数据。当用户提供了交易所代码、产品代码、合约号和商品类型时，调用此工具获取合约信息。对于期权合约，还需要提供行权价。",
        "parameters": {
            "type": "object",
            "properties": {
                "ExchangeCode": {
                    "type": "string", 
                    "description": "交易所代码，必填项。例如：CME。"
                },
                "ProductCode": {
                    "type": "string",
                    "description": "商品代码，必填项。例如：CL。"
                },
                "commodityType": {
                    "type": "string",
                    "enum": ["F", "O"],
                    "description": "商品类型，必填项。期货用“F”表示，期权用“O”表示。"
                },
                "ContractNo": {
                    "type": "string",
                    #"pattern":"^(?:[0-9]{2})(0[1-9]|1[0-2])$",
                    "description": "合约号，必填项。例如：2405表示2024年5月份的合约，LME（伦敦金属交易）使用3M表示。"
                },
                "strikePrice": {
                    "type": "number",
                    "description": "行权价，期权合约必填。"
                },
                #"putCall": {
                #    "type": "string",
                #    "enum": ["C", "P"],
                #    "description": "看涨看跌,选填项。"
                #}

            },
            "required": ["ExchangeCode", "commodityType","ProductCode", "ContractNo"],
            "if": {
                "properties": {
                  "commodityType": { "const": "O" }
                  }
                },
              "then": {
                "required": ["strikePrice"]
              }

        }
    }
}
    ,
        {
    "type": "function",
    "function": {
        "name": "business_question",
        "description": "适用于回答用户提出的除查询合约数据以外的其他问题。对于非合约查询问题，请使用 'business_question' 工具。",
        "parameters": {
            "type": "object",
            "properties": {
                "question": {
                    "type": "string",
                    "description": "用户提问。"
                }
            },
            "required": ["question"]
        }
    }
}]

SystemPrompt = [
                    {"role": "system", "content": "你是上海直达软件公司训练的智能助手小达，能够帮助客户查询合约信息以及回答公司相关产品和业务方面的问题。"},
                    {"role": "system", "content": "不要假设或猜测传入函数的参数值。如果用户的描述不明确，请主动要求用户提供必要信息，以确保查询结果的准确性。"},
                    {"role": "system", "content": "你应该使用客户提问时的语种进行交流。"},
                    {"role": "system", "content": "如果用户提出的问题不是关于查询合约数据，请使用 'business_question'工具。这类问题通常包括公司产品、服务、业务流程、技术等方面的询问。"}
               ]

ToolPrompt=f"根据以下中括号内容：[knowledge]，详细回答以下小括号的问题：(question)。如果中括号内的信息不足以回答问题，请回答'不知道'，并表明你的专长。"

ONLINE_LLM_MODEL = {
    "AzureOpenAI": {
        "model_name": "gpt-4o",
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
    "top_k":2,
    "fetch_k":20,
    "min_score":0.2,
    "mapping_min_score":0.3
    }
TextSplitterCfg={
    "chunksize":600,
    "overlap":20
    }

hostinfo={"hostname":"192.168.200.57","port":"8000"}

CompleteionsPara={"temperature":0.2,"max_tokens":500}
ChatRound=5
wordsnum=300
javaapi="http://192.168.200.10:16001/chatGPT/contractInfo"
#超过24h没有交流，重置该Session的上下文
reste_session_interval=24

contentFilterAnswer=[
    "我不能回答关于仇恨、性、暴力和自残相关的问题，对不起！",
    "抱歉，我不能回应与仇恨、性、暴力和自残有关的内容。",
    "很抱歉，关于仇恨、性、暴力和自残的问题我无法回答。",
    "对不起，我不回答涉及仇恨、性、暴力和自残的内容。",
    "抱歉，我拒绝回应任何涉及仇恨、性、暴力和自残的话题。",
    "对不起，我无法回答涉及仇恨、性、暴力和自残的问题。",
    "抱歉，我不会回答任何关于仇恨、性、暴力和自残的内容。",
    "很抱歉，我拒绝回应关于仇恨、性、暴力和自残的问题。",
    "对不起，关于仇恨、性、暴力和自残的相关内容我不予回答。",
    "抱歉，我不回答涉及仇恨、性、暴力和自残的话题。",
    "很抱歉，我不能回应涉及仇恨、性、暴力和自残的内容。",
    "对不起，我拒绝回答关于仇恨、性、暴力和自残的问题。",
    "抱歉，我不回答关于仇恨、性、暴力和自残的任何问题。",
    "很抱歉，我不回答涉及仇恨、性、暴力和自残的相关内容。",
    "对不起，我不能回答关于仇恨、性、暴力和自残的任何内容。",
    "抱歉，涉及仇恨、性、暴力和自残的问题我无法回答。",
    "对不起，我不回答关于仇恨、性、暴力和自残的任何问题。",
    "抱歉，我不能回应与仇恨、性、暴力和自残有关的任何问题。",
    "很抱歉，我无法回应涉及仇恨、性、暴力和自残的问题。",
    "对不起，涉及仇恨、性、暴力和自残的内容我不能回答。",
    "很抱歉，我无法解答涉及仇恨、性、暴力和自残的任何问题。",
    "抱歉，我不能处理与仇恨、性、暴力和自残相关的内容。",
    "对不起，涉及仇恨、性、暴力和自残的话题我无法回答。",
    "很抱歉，我不提供关于仇恨、性、暴力和自残的回答。",
    "抱歉，任何关于仇恨、性、暴力和自残的内容我都不能回应。",
    "对不起，我不回答任何涉及仇恨、性、暴力和自残的问题。",
    "很抱歉，我无法回应仇恨、性、暴力和自残相关的内容。",
    "抱歉，我不能回答有关仇恨、性、暴力和自残的任何问题。",
    "对不起，我不能解答涉及仇恨、性、暴力和自残的话题。",
    "很抱歉，关于仇恨、性、暴力和自残的问题我无法回应。"
]

inneralError="发生内部异常，请联系技术支持！"