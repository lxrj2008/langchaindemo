
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