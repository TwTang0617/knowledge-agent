from core.llm_client import LLMClient


class FinalAnswerGenerator:

    def __init__(self):
        self.llm_client = LLMClient()

    def generate(self, user_input: str, steps: list[dict]) -> str:

        prompt = f"""
你是一个 Agent 最终答案生成器。

你的任务是根据用户原始问题，以及 Agent 执行过程中得到的工具结果，
生成一个简洁、准确、自然的最终回答。

要求：

1. 不要编造工具结果中不存在的信息。
2. 如果涉及公司制度，以知识库工具结果为准。
3. 如果涉及计算，以 calculator 的结果为准。
4. 不要提到“Planner”“ToolExecutor”“Observation”等内部实现。
5. 直接回答用户问题。
6. 如果工具结果中包含来源信息，可以保留来源。
7. 如果某个工具执行失败，并且后续没有成功结果，
请根据错误信息向用户解释为什么无法完成，
不要假装工具执行成功。
8. 不要暴露内部异常堆栈、Planner、ToolExecutor 等实现细节。
只需要用用户能理解的语言解释。

用户原始问题：

{user_input}

Agent执行步骤：

{steps}

请生成最终答案。
"""

        return self.llm_client.chat(prompt, temperature=0)
