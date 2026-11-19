from services.rag_service import RAGService


class KnowledgeTool:

    def __init__(self):
        self.rag_service = RAGService()

    def run(self, query: str) -> dict:

        answer = self.rag_service.answer(query)

        return {"success": True, "result": answer}


if __name__ == "__main__":

    tool = KnowledgeTool()

    result = tool.run("报销超过多少钱需要领导审批？")

    print(result)
