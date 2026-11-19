from tools.knowledge_tool import KnowledgeTool
from tools.calculator_tool import CalculatorTool


class ToolExecutor:

    def __init__(self):

        self.tools = {"knowledge_qa": KnowledgeTool(), "calculator": CalculatorTool()}

    def execute(self, tool_name: str, args: dict) -> dict:

        tool = self.tools.get(tool_name)

        if tool is None:
            return {"success": False, "error": f"未知工具: {tool_name}"}

        try:

            result = tool.run(**args)

            return result

        except TypeError as e:

            return {"success": False, "error": f"工具参数错误: {str(e)}"}

        except Exception as e:

            return {"success": False, "error": f"工具执行失败: {str(e)}"}


if __name__ == "__main__":

    executor = ToolExecutor()

    result = executor.execute("knowledge_qa", {"query": "报销超过多少钱需要领导审批？"})

    print(result)
