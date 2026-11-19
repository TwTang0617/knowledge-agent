class TextSplitter:

    def split(self, text: str, chunk_size: int = 50, overlap: int = 10):

        if overlap >= chunk_size:
            raise ValueError("overlap 必须小于 chunk_size")

        chunks = []

        start = 0

        while start < len(text):

            end = start + chunk_size

            chunk = text[start:end]

            chunks.append(chunk)

            start = end - overlap

        return chunks

    def split_by_paragraph(self, text: str):

        paragraphs = text.split("\n\n")

        chunks = []

        for paragraph in paragraphs:
            paragraph = paragraph.strip()

            if paragraph:
                chunks.append(paragraph)

        return chunks


if __name__ == "__main__":

    from services.document_loader import DocumentLoader

    loader = DocumentLoader()

    text = loader.load("data/company_handbook.txt")

    splitter = TextSplitter()

    chunks = splitter.split_by_paragraph(text)

    for index, chunk in enumerate(chunks):
        print(f"Chunk {index + 1}:")
        print(chunk)
        print("--------------------")
