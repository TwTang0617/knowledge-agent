from tools.tool_registry import TOOLS


class PlanValidator:

    def validate(self, plan: dict) -> dict:

        # 1. plan 必须是 dict
        if not isinstance(plan, dict):
            return {
                "success": False,
                "tool_name": "none",
                "args": {},
                "message": "规划结果不是字典",
            }

        # 2. 取出 tool_name 和 args
        tool_name = plan.get("tool_name", "none")
        args = plan.get("args", {})

        # 3. args 必须是 dict
        if not isinstance(args, dict):
            return {
                "success": False,
                "tool_name": "none",
                "args": {},
                "message": "args 必须是字典",
            }

        # 4. none 是合法的
        if tool_name == "none":
            return {"success": True, "tool_name": "none", "args": {}, "message": None}

        # 5. tool_name 必须存在于工具注册表
        if tool_name not in TOOLS:
            return {
                "success": False,
                "tool_name": "none",
                "args": {},
                "message": f"未知工具: {tool_name}",
            }

        # 6. 通过校验
        return {"success": True, "tool_name": tool_name, "args": args, "message": None}


if __name__ == "__main__":

    validator = PlanValidator()

    test_plans = [
        {"tool_name": "knowledge_qa", "args": {"query": "报销超过多少钱需要审批？"}},
        {"tool_name": "search", "args": {}},
        {"tool_name": "none", "args": {}},
        {"tool_name": "knowledge_qa", "args": "错误参数"},
    ]

    for plan in test_plans:

        print("\n====================")
        print("原始规划:", plan)

        result = validator.validate(plan)

        print("校验结果:", result)
