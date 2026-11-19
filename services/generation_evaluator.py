import json

from core.llm_client import LLMClient
from services.rag_service import RAGService


class GenerationEvaluator:

    def __init__(self):
        self.rag_service = RAGService()
        self.llm_client = LLMClient()

    def evaluate_answer(
        self, query: str, context: str, answer: str, expected_answerable: bool
    ) -> dict:

        prompt = f"""
你是一个 RAG 回答质量评估器。

请严格根据下面提供的检索证据评估系统回答。

用户问题：
{query}

检索到的有效参考资料：
{context}

系统回答：
{answer}

这个问题理论上是否应该可以根据知识库回答：
{expected_answerable}

请判断以下三项：

1. answer_relevance
系统回答是否直接回答了用户问题。

2. faithfulness
系统回答中的事实是否能够被“检索到的有效参考资料”支持。
如果回答包含参考资料中不存在的事实，应返回 false。
不要使用自己的常识补充证据。

3. refusal_correctness
如果 expected_answerable=False：
系统是否正确拒绝回答。

如果 expected_answerable=True：
这一项返回 true。

只返回 JSON，格式必须是：

{{
    "answer_relevance": true,
    "faithfulness": true,
    "refusal_correctness": true
}}
"""

        result = self.llm_client.chat(prompt, temperature=0).strip()

        print("评估模型原始输出:")
        print(result)

        try:
            return json.loads(result)

        except json.JSONDecodeError:

            print("评估结果 JSON 解析失败")

            return {
                "answer_relevance": False,
                "faithfulness": False,
                "refusal_correctness": False,
            }

    def run(self):

        test_cases = [
            {"query": "我一年能休几天？", "expected_answerable": True},
            {"query": "报销超过多少钱需要领导审批？", "expected_answerable": True},
            {"query": "每周最多能远程办公几天？", "expected_answerable": True},
            {"query": "公司春节放几天假？", "expected_answerable": False},
            {"query": "公司几点上班？", "expected_answerable": False},
        ]

        relevance_correct = 0
        faithfulness_correct = 0
        refusal_correct = 0

        total = len(test_cases)

        for case in test_cases:

            query = case["query"]
            expected_answerable = case["expected_answerable"]

            print("\n============================")
            print("问题:", query)

            # 不再只调用 answer()
            # 现在拿完整 RAG Trace
            trace = self.rag_service.answer_with_trace(query)

            # 从 Trace 中分别拿最终回答和真实 Context
            answer = trace["answer"]
            context = trace["context"]

            print("系统回答:")
            print(answer)

            print("实际使用的 Context:")
            print(context)

            print("来源:")
            print(trace["sources"])

            # 把真实 Context 一起交给 Judge
            evaluation = self.evaluate_answer(
                query, context, answer, expected_answerable
            )

            print("评估结果:")
            print(evaluation)

            # -------------------------
            # 统计三个指标
            # -------------------------

            if evaluation["answer_relevance"]:
                relevance_correct += 1

            if evaluation["faithfulness"]:
                faithfulness_correct += 1

            if evaluation["refusal_correctness"]:
                refusal_correct += 1

        # -------------------------
        # 最终统计
        # -------------------------

        print("\n============================")
        print("Generation Evaluation")

        print("测试总数:", total)

        print("Answer Relevance 正确数量:", relevance_correct)

        print("Faithfulness 正确数量:", faithfulness_correct)

        print("Refusal 正确数量:", refusal_correct)

        print("Answer Relevance Accuracy:", relevance_correct / total)

        print("Faithfulness Accuracy:", faithfulness_correct / total)

        print("Refusal Accuracy:", refusal_correct / total)


if __name__ == "__main__":

    evaluator = GenerationEvaluator()

    evaluator.run()
