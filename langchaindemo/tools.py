
tools = [
        {
            "type": "function",
            "function": {
                "name": "get_current_weather",
                "description": "获取指定地区的天气情况",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "location": {
                            "type": "string",
                            "description": "特定的城市, 比如上海、北京、广州",
                        },
                        "unit": {"type": "string", "enum": ["摄氏度（℃）", "华氏度（℉）"]},
                    },
                    "required": ["location"],
                },
            },
        },
        {
    "type": "function",
    "function": {
        "name": "get_contract_info",
        "description": "你是一个专业的合约、产品查助手，能够为客户查询特定的产品或合约信息",
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
                }
            },
            "required": ["exchange_code", "clearing_code", "contract_code"]
        }
    }
}

    ]