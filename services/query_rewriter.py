from core.llm_client import LLMClient


class QueryRewriter:

    def __init__(self):
        self.llm_client = LLMClient()

    def rewrite(self, query: str) -> str:

        prompt = f"""
你是一个企业知识库检索问题改写器。

知识库目前包含这些主题：
- 年假制度
- 报销制度
- 远程办公制度
- 培训制度
- 加班制度

请把用户问题改写成更明确、适合知识库检索的问题。

要求：
1. 保留用户原始意图
2. 不要回答问题
3. 不要编造用户没有提供的事实
4. 如果用户问题明显对应某个知识库主题，可以使用该主题中的标准术语
5. 如果无法确定对应主题，就只做语言规范化，不要强行映射
6. 只返回改写后的问题，不要解释

用户问题：
{query}

改写后的问题：
"""

        rewritten_query = self.llm_client.chat(prompt).strip()

        print("原始问题:", query)
        print("改写问题:", rewritten_query)

        return rewritten_query


if __name__ == "__main__":

    rewriter = QueryRewriter()

    print(rewriter.rewrite("我一年能休几天？"))

    print(rewriter.rewrite("公司给不给员工学习的钱？"))

    print(rewriter.rewrite("公司春节放几天假？"))
