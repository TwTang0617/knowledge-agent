class DocumentLoader:

    def load(self, file_path: str) -> str:

        with open(file_path, "r", encoding="utf-8") as file:
            content = file.read()

        return content


if __name__ == "__main__":

    loader = DocumentLoader()

    content = loader.load("data/company_handbook.txt")

    print(content)
