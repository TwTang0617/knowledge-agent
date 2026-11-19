import json

from core.llm_client import LLMClient
from tools.tool_registry import TOOLS


class AgentPlanner:

    def __init__(self):
        self.llm_client = LLMClient()

    def build_prompt(self, message: str, observation: str | None = None) -> str:

        observation_text = observation if observation else "暂无"

        return f"""
你是一个 Agent Planner。

你的任务是根据用户目标，以及可能存在的上一步工具结果，
决定下一步应该做什么。

当前可用工具：

{TOOLS}

用户原始问题：

{message}

上一步工具结果：

{observation_text}

规则：

1. 如果用户询问公司内部制度、员工手册、报销、年假、培训、
远程办公、加班调休等公司知识，
使用 knowledge_qa。

2. 如果用户要求进行明确数学计算，
使用 calculator。

3. 如果用户问题已经能够根据上一步工具结果直接完成，
返回 none。

4. 如果上一步工具结果中提供了一个数字，
而用户还要求继续计算，
应该选择 calculator。

例如：

用户问题：
公司年假有多少天，如果我已经休了5天，还剩多少天？

上一步工具结果：
员工入职满一年后，每年享有12天带薪年假。

下一步应该输出：

{{
    "tool_name": "calculator",
    "args": {{
        "expression": "12 - 5"
    }}
}}

5. 如果用户问题需要多个步骤完成，
每次只规划当前下一步，不要一次完成整个任务。

当当前步骤需要查询公司知识库时，
选择 knowledge_qa。

knowledge_qa 的 query 只保留“当前需要从知识库获取的信息”，
不要包含后续计算、比较或其他任务。

例如：

用户问题：
公司年假有多少天，如果我已经休了5天，还剩多少天？

第一次应该输出：

{{
    "tool_name": "knowledge_qa",
    "args": {{
        "query": "公司年假有多少天？"
    }}
}}

6. calculator 参数格式：

{{
    "tool_name": "calculator",
    "args": {{
        "expression": "12 - 5"
    }}
}}

7. 如果不需要继续调用工具：

{{
    "tool_name": "none",
    "args": {{}}
}}

8. 如果“上一步工具结果”包含工具执行失败或错误信息，
你需要根据错误重新决定下一步。

错误处理规则：

- 如果错误可以通过修改参数解决，
  重新选择合适的工具和参数。

- 如果可以换其他工具完成任务，
  选择其他工具。

- 如果错误本身说明任务无法继续完成，
  返回 none。

- 不要在完全相同的错误条件下，
  重复调用相同工具和相同参数。

例如：

用户问题：
10 / 0 等于多少？

上一步工具结果：
工具 calculator 执行失败：计算失败: division by zero

应该输出：

{{
    "tool_name": "none",
    "args": {{}}
}}

9. knowledge_qa 参数必须是：

{{
    "query": "需要查询的问题"
}}

10. calculator 参数必须是：

{{
    "expression": "数学表达式"
}}

11. tool_name 只能是：

knowledge_qa
calculator
none

12. 只返回 JSON。

不要返回解释。
不要返回 Markdown。
不要使用代码块。
不要输出 JSON 以外的任何内容。
"""

    def plan(self, message: str, observation: str | None = None) -> dict:

        prompt = self.build_prompt(message, observation)

        result_text = self.llm_client.chat(prompt, temperature=0).strip()

        print("模型原始规划结果:", result_text)

        # 去掉模型偶尔生成的 Markdown 代码块
        if result_text.startswith("```"):

            result_text = result_text.replace("```json", "")

            result_text = result_text.replace("```", "")

            result_text = result_text.strip()

        try:

            plan = json.loads(result_text)

            return plan

        except json.JSONDecodeError:

            return {
                "tool_name": "none",
                "args": {},
                "error": ("Planner 返回的不是合法 JSON"),
                "raw_output": result_text,
            }


if __name__ == "__main__":

    planner = AgentPlanner()

    tests = [
        {"message": "公司年假有多少天？", "observation": None},
        {"message": "12 * 37 等于多少？", "observation": None},
        {
            "message": "公司年假有多少天，如果我已经休了5天，还剩多少天？",
            "observation": None,
        },
        {
            "message": "公司年假有多少天，如果我已经休了5天，还剩多少天？",
            "observation": "员工入职满一年后，每年享有12天带薪年假。",
        },
        {
            "message": "10 / 0 等于多少？",
            "observation": "工具 calculator 执行失败：计算失败: division by zero",
        },
        {"message": "什么是 AI Agent？", "observation": None},
    ]

    for index, test in enumerate(tests, start=1):

        print(f"\n===== Planner Test {index} =====")

        print("用户问题:", test["message"])

        print("Observation:", test["observation"])

        plan = planner.plan(test["message"], test["observation"])

        print("Planner结果:", plan)
