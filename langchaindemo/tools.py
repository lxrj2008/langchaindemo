# coding=gbk
tools = [
        {
            "type": "function",
            "function": {
                "name": "get_current_weather",
                "description": "��ȡָ���������������",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "location": {
                            "type": "string",
                            "description": "�ض��ĳ���, �����Ϻ�������������",
                        },
                        "unit": {"type": "string", "enum": ["���϶ȣ��棩", "���϶ȣ��H��"]},
                    },
                    "required": ["location"],
                },
            },
        },
        {
    "type": "function",
    "function": {
        "name": "get_contract_info",
        "description": "����һ��רҵ�ĺ�Լ����Ʒ�����֣��ܹ�Ϊ�ͻ���ѯ�ض��Ĳ�Ʒ���Լ��Ϣ",
        "parameters": {
            "type": "object",
            "properties": {
                "exchange_code": {
                    "type": "string",
                    "description": "����������,����CME"
                },
                "clearing_code": {
                    "type": "string",
                    "description": "������룬����MNQ"
                },
                "contract_code": {
                    "type": "string",
                    "description": "��Լ���ڣ�����20230900"
                }
            },
            "required": ["exchange_code", "clearing_code", "contract_code"]
        }
    }
}

    ]