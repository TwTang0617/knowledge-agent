from sentence_transformers import SentenceTransformer


class EmbeddingService:

    def __init__(self):
        self.model = SentenceTransformer("BAAI/bge-small-zh-v1.5")

    def embed(self, text: str) -> list[float]:

        vector = self.model.encode(text, normalize_embeddings=True)

        return vector.tolist()

    def similarity(self, vector1: list[float], vector2: list[float]) -> float:

        score = sum(a * b for a, b in zip(vector1, vector2))

        return score

    def embed_query(self, query: str) -> list[float]:

        query_text = f"为这个句子生成表示以用于检索相关文章：{query}"

        return self.embed(query_text)

    def embed_document(self, text: str) -> list[float]:

        return self.embed(text)


if __name__ == "__main__":

    embedding_service = EmbeddingService()

    query_vector = embedding_service.embed("我一年能休几天？")

    vacation_vector = embedding_service.embed(
        "员工入职满一年后，每年享有10天带薪年假。"
    )

    reimbursement_vector = embedding_service.embed(
        "单笔报销金额超过500元，需要部门负责人审批。"
    )

    vacation_score = embedding_service.similarity(query_vector, vacation_vector)

    reimbursement_score = embedding_service.similarity(
        query_vector, reimbursement_vector
    )

    print("年假相似度:", vacation_score)
    print("报销相似度:", reimbursement_score)
