from core.llm_client import LLMClient

from services.document_loader import DocumentLoader
from services.text_splitter import TextSplitter
from services.vector_retriever import VectorRetriever
from services.relevance_checker import RelevanceChecker
from services.query_rewriter import QueryRewriter


class RAGService:

    def __init__(self):
        self.loader = DocumentLoader()
        self.splitter = TextSplitter()
        self.retriever = VectorRetriever()
        self.llm_client = LLMClient()
        self.relevance_checker = RelevanceChecker()
        self.query_rewriter = QueryRewriter()

        text = self.loader.load("data/company_handbook.txt")

        chunks = self.splitter.split_by_paragraph(text)

        self.retriever.build_index(text, chunks)

    def answer(self, query: str) -> str:

        rewritten_query = self.query_rewriter.rewrite(query)

        print("用于检索的问题:", rewritten_query)

        results = self.retriever.retrieve(rewritten_query, top_k=2)

        relevant_chunks = []

        for result in results:

            chunk = result["text"]
            metadata = result["metadata"]

            print("\n候选 Chunk:")
            print(chunk)
            print("来源:", metadata)

            is_relevant = self.relevance_checker.check(rewritten_query, chunk)

            print("是否保留:", is_relevant)

            if is_relevant:
                relevant_chunks.append({"text": chunk, "metadata": metadata})

        if not relevant_chunks:
            return "根据当前知识库无法确定。"

        context = "\n\n".join(item["text"] for item in relevant_chunks)

        prompt = f"""
你是一个企业知识库问答助手。

请根据下面提供的参考资料回答用户问题。

要求：
1. 只回答和用户问题直接相关的内容
2. 不要扩展回答参考资料中与问题无关的信息
3. 如果参考资料中没有足够的信息，请明确回答：
“根据当前知识库无法确定。”
4. 不要编造参考资料中不存在的信息

参考资料：
{context}

用户问题：
{query}

回答：
"""

        answer = self.llm_client.chat(prompt)

        sources = []

        for item in relevant_chunks:

            metadata = item["metadata"]

            source_text = f"{metadata['source']} " f"(Chunk {metadata['chunk_id']})"

            sources.append(source_text)

        source_text = "\n".join(sources)

        return f"{answer}\n\n来源：\n{source_text}"

    def answer_with_trace(self, query: str) -> dict:

        rewritten_query = self.query_rewriter.rewrite(query)

        results = self.retriever.retrieve(rewritten_query, top_k=2)

        relevant_chunks = []

        for result in results:

            chunk = result["text"]
            metadata = result["metadata"]

            is_relevant = self.relevance_checker.check(rewritten_query, chunk)

            if is_relevant:
                relevant_chunks.append({"text": chunk, "metadata": metadata})

        if not relevant_chunks:

            return {
                "query": query,
                "rewritten_query": rewritten_query,
                "retrieved_chunks": results,
                "relevant_chunks": [],
                "context": "",
                "answer": "根据当前知识库无法确定。",
                "sources": [],
            }

        context = "\n\n".join(item["text"] for item in relevant_chunks)

        prompt = f"""
    你是一个企业知识库问答助手。

    请根据下面提供的参考资料回答用户问题。

    要求：
    1. 只回答和用户问题直接相关的内容
    2. 不要扩展回答参考资料中与问题无关的信息
    3. 如果参考资料中没有足够的信息，请明确回答：
    “根据当前知识库无法确定。”
    4. 不要编造参考资料中不存在的信息

    参考资料：
    {context}

    用户问题：
    {query}

    回答：
    """

        answer = self.llm_client.chat(prompt)

        sources = []

        for item in relevant_chunks:

            metadata = item["metadata"]

            sources.append(
                {"source": metadata["source"], "chunk_id": metadata["chunk_id"]}
            )

        return {
            "query": query,
            "rewritten_query": rewritten_query,
            "retrieved_chunks": results,
            "relevant_chunks": relevant_chunks,
            "context": context,
            "answer": answer,
            "sources": sources,
        }


if __name__ == "__main__":

    rag_service = RAGService()

    queries = ["我一年能休几天？", "报销超过多少钱需要领导审批？", "公司春节放几天假？"]

    for query in queries:

        print("\n============================")
        print("用户问题:", query)

        answer = rag_service.answer(query)

        print("RAG回答:")
        print(answer)
