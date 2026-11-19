import json
import os


class VectorStore:

    def __init__(self):
        self.items = []

    def add(self, text: str, vector: list[float], metadata: dict):

        self.items.append({"text": text, "vector": vector, "metadata": metadata})

    def get_all(self):
        return self.items

    def save(self, file_path: str, document_hash: str):

        data = {"document_hash": document_hash, "items": self.items}

        with open(file_path, "w", encoding="utf-8") as file:
            json.dump(data, file, ensure_ascii=False)

    def load(self, file_path: str):

        if not os.path.exists(file_path):
            return None

        with open(file_path, "r", encoding="utf-8") as file:
            data = json.load(file)

        self.items = data["items"]

        return data["document_hash"]
