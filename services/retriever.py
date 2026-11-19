class Retriever:

    def retrieve(self, query: str, chunks: list[str]) -> list[str]:

        results = []

        for chunk in chunks:

            if query in chunk:
                results.append(chunk)

        return results


if __name__ == "__main__":

    from services.document_loader import DocumentLoader
    from services.text_splitter import TextSplitter

    loader = DocumentLoader()
    splitter = TextSplitter()
    retriever = Retriever()

    text = loader.load("data/company_handbook.txt")

    chunks = splitter.split_by_paragraph(text)

    query = "我一年能休几天"

    results = retriever.retrieve(query, chunks)

    for result in results:
        print(result)
        print("--------------------")
