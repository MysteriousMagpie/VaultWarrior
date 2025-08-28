from sentence_transformers import SentenceTransformer
import numpy as np
from typing import List, Union

_model_cache: Union[SentenceTransformer, None] = None

def _get_model():
    global _model_cache
    if _model_cache is None:
        _model_cache = SentenceTransformer('all-MiniLM-L6-v2')
    return _model_cache

def create_embeddings(text: str) -> List[float]:
    """Return embedding list for single text (test helper API)."""
    emb = _get_model().encode([text], convert_to_numpy=True)[0]
    return emb.tolist()

class Embeddings:
    def __init__(self, model_name='all-MiniLM-L6-v2'):
        self.model = SentenceTransformer(model_name)

    def create_embeddings(self, texts):
        return self.model.encode(texts, convert_to_tensor=True)

    def save_embeddings(self, embeddings, file_path):
        np.save(file_path, embeddings.cpu().numpy())

    def load_embeddings(self, file_path):
        return np.load(file_path)