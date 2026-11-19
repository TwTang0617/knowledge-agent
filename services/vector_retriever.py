import hashlib

from services.embedding_service import EmbeddingService
from services.vector_store import VectorStore


class VectorRetriever:

    def __init__(self):
        self.embedding_service = EmbeddingService()
        self.vector_store = VectorStore()
        self.index_path = "data/vector_index.json"

    def calculate_hash(self, text: str) -> str:

        return hashlib.sha256(text.encode("utf-8")).hexdigest()

    def build_index(self, text: str, chunks: list[str]):

        current_hash = self.calculate_hash(text)

        saved_hash = self.vector_store.load(self.index_path)

        if saved_hash == current_hash:
            print("文档未变化，已加载已有向量索引")
            return

        print("文档发生变化或索引不存在，开始重新构建...")

        self.vector_store.items = []

        for index, chunk in enumerate(chunks):

            vector = self.embedding_service.embed_document(chunk)

            metadata = {"source": "company_handbook.txt", "chunk_id": index + 1}

            self.vector_store.add(chunk, vector, metadata)

        self.vector_store.save(self.index_path, current_hash)

        print("向量索引重新构建并保存完成")

    def retrieve(self, query: str, top_k: int = 2) -> list[dict]:

        query_vector = self.embedding_service.embed_query(query)

        scored_chunks = []

        for item in self.vector_store.get_all():

            score = self.embedding_service.similarity(query_vector, item["vector"])

            scored_chunks.append(
                {"text": item["text"], "score": score, "metadata": item["metadata"]}
            )

        scored_chunks.sort(key=lambda item: item["score"], reverse=True)

        return scored_chunks[:top_k]


if __name__ == "__main__":

    from services.document_loader import DocumentLoader
    from services.text_splitter import TextSplitter

    loader = DocumentLoader()
    splitter = TextSplitter()
    retriever = VectorRetriever()

    text = loader.load("data/company_handbook.txt")

    chunks = splitter.split_by_paragraph(text)

    retriever.build_index(text, chunks)

    queries = [
        "我一年能休几天？",
        "公司给不给员工学习的钱？",
        "报销超过多少钱需要领导审批？",
        "公司春节放几天假？",
    ]

    for query in queries:

        print("\n============================")
        print("用户问题:", query)

        results = retriever.retrieve(query, top_k=2)

        for index, result in enumerate(results):
            print(f"\nTop {index + 1}")
            print("相似度:", result["score"])
            print("内容:")
            print(result["text"])
