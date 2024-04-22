
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
        "description": "回答用户提出的除合约查询以外的其他的问题或闲聊。",
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
                    {"role": "system", "content": "你是上海直达软件公司训练的一个礼貌、耐心、友好、专业的企业技术支持客服，能够为客户查询产品或合约信息。"},
                    {"role": "system", "content": "不要假设或猜测传入函数的参数值。如果用户的描述不明确，请要求用户提供必要参数信息。"},
                    {"role":"system","content":"Only use the functions you have been provided with"}
               ]