from services.document_loader import DocumentLoader
from services.text_splitter import TextSplitter
from services.vector_retriever import VectorRetriever
from services.query_rewriter import QueryRewriter
from services.relevance_checker import RelevanceChecker


class RAGEvaluator:

    def __init__(self):
        self.loader = DocumentLoader()
        self.splitter = TextSplitter()
        self.retriever = VectorRetriever()
        self.query_rewriter = QueryRewriter()
        self.relevance_checker = RelevanceChecker()

        text = self.loader.load("data/company_handbook.txt")

        chunks = self.splitter.split_by_paragraph(text)

        self.retriever.build_index(text, chunks)

    def evaluate(self):

        test_cases = [
            # =========================
            # 1. 年假制度
            # =========================
            {
                "query": "员工每年有多少天年假？",
                "expected_chunk_id": 1,
                "expected_answerable": True,
            },
            {
                "query": "我一年能休几天？",
                "expected_chunk_id": 1,
                "expected_answerable": True,
            },
            {
                "query": "公司每年给员工多少天带薪假？",
                "expected_chunk_id": 1,
                "expected_answerable": True,
            },
            {
                "query": "入职满一年以后有多少天年假？",
                "expected_chunk_id": 1,
                "expected_answerable": True,
            },
            # =========================
            # 2. 报销制度
            # =========================
            {
                "query": "报销超过多少钱需要领导审批？",
                "expected_chunk_id": 2,
                "expected_answerable": True,
            },
            {
                "query": "单笔报销到什么金额需要负责人审批？",
                "expected_chunk_id": 2,
                "expected_answerable": True,
            },
            {
                "query": "报销600元需要审批吗？",
                "expected_chunk_id": 2,
                "expected_answerable": True,
            },
            {
                "query": "500元以上的报销怎么处理？",
                "expected_chunk_id": 2,
                "expected_answerable": True,
            },
            # =========================
            # 3. 远程办公
            # =========================
            {
                "query": "每周最多能远程办公几天？",
                "expected_chunk_id": 3,
                "expected_answerable": True,
            },
            {
                "query": "一周能在家办公几天？",
                "expected_chunk_id": 3,
                "expected_answerable": True,
            },
            {
                "query": "公司允许每周远程办公多久？",
                "expected_chunk_id": 3,
                "expected_answerable": True,
            },
            # =========================
            # 4. 培训预算
            # =========================
            {
                "query": "公司给不给员工学习的钱？",
                "expected_chunk_id": 4,
                "expected_answerable": True,
            },
            {
                "query": "员工每年有多少培训预算？",
                "expected_chunk_id": 4,
                "expected_answerable": True,
            },
            {
                "query": "公司会报销培训费用吗？",
                "expected_chunk_id": None,
                "expected_answerable": False,
            },
            # =========================
            # 5. 加班调休
            # =========================
            {
                "query": "加班以后可以调休吗？",
                "expected_chunk_id": 5,
                "expected_answerable": True,
            },
            {
                "query": "工作日加班能不能申请补休？",
                "expected_chunk_id": 5,
                "expected_answerable": True,
            },
            # =========================
            # 6. 无答案 / 干扰问题
            # =========================
            {
                "query": "公司春节放几天假？",
                "expected_chunk_id": None,
                "expected_answerable": False,
            },
            {
                "query": "公司几点上班？",
                "expected_chunk_id": None,
                "expected_answerable": False,
            },
            {
                "query": "公司有没有住房补贴？",
                "expected_chunk_id": None,
                "expected_answerable": False,
            },
            {
                "query": "员工有多少天病假？",
                "expected_chunk_id": None,
                "expected_answerable": False,
            },
        ]

        top1_correct = 0
        recall_correct = 0
        answerable_count = 0

        answerability_correct = 0

        false_positive = 0
        false_negative = 0

        for case in test_cases:

            query = case["query"]
            expected_chunk_id = case["expected_chunk_id"]
            expected_answerable = case["expected_answerable"]

            print("\n============================")
            print("原始问题:", query)

            # 1. Query Rewrite
            rewritten_query = self.query_rewriter.rewrite(query)

            print("用于检索的问题:", rewritten_query)

            # 2. Retriever
            results = self.retriever.retrieve(rewritten_query, top_k=2)

            predicted_chunk_ids = [result["metadata"]["chunk_id"] for result in results]

            print("Top-2 Chunk:", predicted_chunk_ids)

            # -------------------------
            # Retriever Evaluation
            # -------------------------

            if expected_chunk_id is not None:

                answerable_count += 1

                predicted_top1_chunk_id = predicted_chunk_ids[0]

                top1_is_correct = predicted_top1_chunk_id == expected_chunk_id

                if top1_is_correct:
                    top1_correct += 1

                is_recalled = expected_chunk_id in predicted_chunk_ids

                if is_recalled:
                    recall_correct += 1

                print("期望 Chunk:", expected_chunk_id)
                print("Top-1 Chunk:", predicted_top1_chunk_id)
                print("Top-1 是否正确:", top1_is_correct)
                print("Top-2 是否召回:", is_recalled)

            else:
                print("期望 Chunk: None")

            # -------------------------
            # Answerability Evaluation
            # -------------------------

            relevant_chunks = []

            for result in results:

                chunk = result["text"]

                is_relevant = self.relevance_checker.check(rewritten_query, chunk)

                if is_relevant:
                    relevant_chunks.append(chunk)

            predicted_answerable = len(relevant_chunks) > 0

            is_answerability_correct = predicted_answerable == expected_answerable

            if is_answerability_correct:
                answerability_correct += 1

            # False Positive
            if predicted_answerable is True and expected_answerable is False:
                false_positive += 1

            # False Negative
            if predicted_answerable is False and expected_answerable is True:
                false_negative += 1

            print("期望可回答:", expected_answerable)
            print("实际可回答:", predicted_answerable)
            print("可回答判断是否正确:", is_answerability_correct)

        # -------------------------
        # 最终指标
        # -------------------------

        print("\n============================")

        if answerable_count > 0:

            top1_accuracy = top1_correct / answerable_count

            top2_recall = recall_correct / answerable_count

            print("有答案测试总数:", answerable_count)
            print("Top-1 正确数量:", top1_correct)
            print("Top-2 召回数量:", recall_correct)
            print("Top-1 Accuracy:", top1_accuracy)
            print("Top-2 Recall:", top2_recall)

        answerability_accuracy = answerability_correct / len(test_cases)

        print("Answerability 正确数量:", answerability_correct)
        print("Answerability Accuracy:", answerability_accuracy)
        print("False Positive:", false_positive)
        print("False Negative:", false_negative)


if __name__ == "__main__":

    evaluator = RAGEvaluator()

    evaluator.evaluate()
