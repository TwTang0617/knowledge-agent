from core.llm_client import LLMClient


class RelevanceChecker:

    def __init__(self):
        self.llm_client = LLMClient()

    def check(self, query: str, context: str) -> bool:

        prompt = f"""
你是一个知识库证据充分性判断器。

你的任务不是回答问题，而是判断参考资料中是否明确包含回答问题所需要的信息。

用户问题：
{query}

参考资料：
{context}

判断规则：
1. 如果参考资料中明确包含问题所询问的信息，返回 yes
2. 如果资料只是主题相关，但缺少问题要求的具体信息，返回 no
3. 不要使用自己的常识
4. 不要要求资料回答用户没有询问的额外信息
5. 只返回 yes 或 no

示例：

问题：
员工每年有多少天年假？

资料：
员工入职满一年后，每年享有10天带薪年假。

结果：
yes

问题：
公司春节放几天假？

资料：
员工入职满一年后，每年享有10天带薪年假。

结果：
no

现在判断：

问题：
{query}

资料：
{context}

结果：
"""

        result = self.llm_client.chat(prompt).strip().lower()

        print("相关性判断结果:", result)

        return result == "yes"


if __name__ == "__main__":

    checker = RelevanceChecker()

    query = "根据公司年假制度，我一年可以休多少天年假？"

    context = """
公司的年假制度：
员工入职满一年后，每年享有10天带薪年假。
"""

    for i in range(3):

        result = checker.check(query, context)

        print(f"第{i + 1}次:", result)
