
tools = [
        {
    "type": "function",
    "function": {
        "name": "get_contract_info",
        "description": "根据交易所代码、清算代码、产品类型和合约日期查询对应的合约或产品信息",
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
                },
                "product_type": {
                    "type": "string",
                    "description": "产品类型，比如FUT（期货）、OOF（期权）"
                }
            },
            "required": ["exchange_code", "clearing_code", "contract_code",'product_type']
        }
    }
}
    ,
        {
    "type": "function",
    "function": {
        "name": "answer_question",
        "description": "回答工具{get_contract_info}以外的其他问题。",
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
                    {"role": "system", "content": "你是上海直达软件公司训练的智能客服小达达。直达软件专注于服务快速增长的全球金融市场,研发全球期货,期权,股票,牛熊证,认股权,基金,衍生品等交易平台、工具和行业解决方案"},
                    {"role": "system", "content": "不要假设或猜测传入函数的参数值。如果用户的描述不明确，请要求用户提供必要参数信息。"},
                    {"role":"system","content":"Only use the functions you have been provided with"}
               ]

ToolPrompt=f"根据知识库内容：[knowledge]，回答以下问题：[question]。如果你觉得知识库内容信息不足以回答这个问题，请回答不知道并且表明你的专长"

ONLINE_LLM_MODEL = {
    "AzureOpenAI": {
        "model_name": "gpt-35-turbo",
        "api_base_url": "https://zdopenai2.openai.azure.com/",
        "api_version":"2024-02-15-preview",
        "api_key": "d4d9c0e614be43da919c5695a818dc41",
        "openai_proxy": "",
        "embedding":"text-embedding-ada-002"
    },
}

SimilaritySearchCfg={
    "top_k":3,
    "fetch_k":20
    }
TextSplitterCfg={
    "chunksize":250,
    "overlap":50
    }

hostinfo={"hostname":"192.168.200.57","port":"8000"}

CompleteionsPara={"temperature":0.3,"max_tokens":1000}
ChatRound=5
wordsnum=300