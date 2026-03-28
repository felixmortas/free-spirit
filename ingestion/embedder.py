import requests

class MistralEmbedder:
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.url = "https://api.mistral.ai/v1/embeddings"

    def embed(self, texts):
        res = requests.post(
            self.url,
            headers={
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            },
            json={
                "model": "mistral-embed",
                "input": texts
            }
        )
        return [d["embedding"] for d in res.json()["data"]]