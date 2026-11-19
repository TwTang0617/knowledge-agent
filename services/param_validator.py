class ParamValidator:

    def validate(self, tool_name: str, args: dict) -> dict:

        if tool_name == "none":
            return {"success": True, "message": None}

        if tool_name == "knowledge_qa":

            query = args.get("query")

            if query is None:
                return {"success": False, "message": "缺少参数: query"}

            if not isinstance(query, str):
                return {"success": False, "message": "参数 query 必须是字符串"}

            if not query.strip():
                return {"success": False, "message": "参数 query 不能为空"}

            return {"success": True, "message": None}

        if tool_name == "calculator":

            expression = args.get("expression")

            if expression is None:
                return {"success": False, "message": "缺少参数: expression"}

            if not isinstance(expression, str):
                return {"success": False, "message": "参数 expression 必须是字符串"}

            if not expression.strip():
                return {"success": False, "message": "参数 expression 不能为空"}

            return {"success": True, "message": None}

        return {"success": False, "message": f"不支持的工具: {tool_name}"}


if __name__ == "__main__":

    validator = ParamValidator()

    test_cases = [
        {"tool_name": "knowledge_qa", "args": {"query": "报销超过多少钱需要审批？"}},
        {"tool_name": "knowledge_qa", "args": {}},
        {"tool_name": "knowledge_qa", "args": {"query": 123}},
        {"tool_name": "knowledge_qa", "args": {"query": ""}},
        {"tool_name": "none", "args": {}},
    ]

    for case in test_cases:

        print("\n====================")
        print("测试:", case)

        result = validator.validate(case["tool_name"], case["args"])

        print("参数校验结果:", result)
