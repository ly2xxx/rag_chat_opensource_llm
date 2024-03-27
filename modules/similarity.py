from sentence_transformers import SentenceTransformer, util
from torch import Tensor

class SimilarityScorer:
    def __init__(self):
        self.model = SentenceTransformer('./models/all-MiniLM-L6-v2')

    def score(self, text1, text2):
        # scoring logic
        embedding_1: Tensor = self.model.encode(text1, convert_to_tensor=True)
        embedding_2: Tensor = self.model.encode(text2, convert_to_tensor=True)
        score = util.pytorch_cos_sim(embedding_1, embedding_2)[0][0].item()
        return score 