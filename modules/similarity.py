import os
import numpy as np
from langchain_ollama import OllamaEmbeddings


class SimilarityScorer:
    """Cosine similarity of two texts using Ollama embeddings.

    Uses the same embedding backend as the rest of the app (no torch /
    sentence-transformers dependency).
    """

    def __init__(self, model="nomic-embed-text"):
        base_url = os.environ.get("OLLAMA_BASE_URL", "http://localhost:11434")
        self.embeddings = OllamaEmbeddings(model=model, base_url=base_url)

    def score(self, text1, text2):
        vec1, vec2 = self.embeddings.embed_documents([text1, text2])
        a, b = np.asarray(vec1), np.asarray(vec2)
        denom = np.linalg.norm(a) * np.linalg.norm(b)
        if denom == 0:
            return 0.0
        return float(np.dot(a, b) / denom)
