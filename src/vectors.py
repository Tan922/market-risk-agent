from sentence_transformers import SentenceTransformer
import faiss
import numpy as np
import pickle
from typing import List, Dict

embed_model = SentenceTransformer("all-MiniLM-L6-v2")

class FaissStore:
    def __init__(self, dim=384, index_path="/data/faiss.index", meta_path="/data/faiss_meta.pkl"):
        self.dim = dim
        self.index_path = index_path
        self.meta_path = meta_path
        # We keep a list of ids -> row mapping.
        self.ids = []
        self.metadata = {}
        try:
            self.index = faiss.read_index(self.index_path)
            with open(self.meta_path, "rb") as f:
                meta = pickle.load(f)
                self.ids = meta.get("ids", [])
                self.metadata = meta.get("metadata", {})
        except Exception:
            self.index = faiss.IndexFlatIP(dim)
            self.ids = []
            self.metadata = {}

    def add(self, doc_id: str, text: str, meta: Dict):
        emb = embed_model.encode([text], convert_to_numpy=True, normalize_embeddings=True)
        self.index.add(emb)
        self.ids.append(doc_id)
        self.metadata[doc_id] = {"text": text, "meta": meta}
        self._persist()

    def _persist(self):
        try:
            faiss.write_index(self.index, self.index_path)
            with open(self.meta_path, "wb") as f:
                pickle.dump({"ids": self.ids, "metadata": self.metadata}, f)
        except Exception:
            # For demo, not failing hard
            pass

    def query(self, query_text: str, k=5):
        q_emb = embed_model.encode([query_text], convert_to_numpy=True, normalize_embeddings=True)
        scores, idxs = self.index.search(q_emb, k)
        docs = []
        for idx in idxs[0]:
            if idx < 0 or idx >= len(self.ids):
                continue
            doc_id = self.ids[idx]
            docs.append(self.metadata.get(doc_id))
        return scores[0].tolist(), docs
