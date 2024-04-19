
tools = [
        {
            "type": "function",
            "function": {
                "name": "get_current_weather",
                "description": "根据城市名称获取对应的天气信息",
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
        "description": "根据交易所代码、清算代码和合约日期查询对应的合约或产品信息",
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