TOOLS = {
    "knowledge_qa": {
        "description": "用于查询公司内部知识库中的制度、政策和员工手册信息",
        "parameters": {
            "query": {"type": "string", "description": "需要查询的知识库问题"}
        },
    },
    "calculator": {
        "description": "用于执行数学计算，例如加减乘除、括号运算等",
        "parameters": {
            "expression": {
                "type": "string",
                "description": "需要计算的数学表达式，例如 12 * 37",
            }
        },
    },
}
