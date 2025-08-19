from sentence_transformers import SentenceTransformer
import numpy as np

class Embeddings:
    def __init__(self, model_name='all-MiniLM-L6-v2'):
        self.model = SentenceTransformer(model_name)

    def create_embeddings(self, texts):
        return self.model.encode(texts, convert_to_tensor=True)

    def save_embeddings(self, embeddings, file_path):
        np.save(file_path, embeddings.cpu().numpy())

    def load_embeddings(self, file_path):
        return np.load(file_path)