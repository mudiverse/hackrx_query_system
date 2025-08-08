import os
import pickle
import numpy as np
from typing import List, Dict, Any, Tuple
import faiss
import google.generativeai as genai
from app.utils.config import Config


def _l2_normalize(vectors: np.ndarray) -> np.ndarray:
    """L2-normalize vectors along axis 1 to enable cosine similarity with inner product index."""
    norms = np.linalg.norm(vectors, axis=1, keepdims=True)
    norms[norms == 0] = 1.0
    return vectors / norms


class EmbeddingService:
    """Service for creating embeddings and managing FAISS index using Gemini."""

    def __init__(self):
        Config.validate()
        genai.configure(api_key=Config.GEMINI_API_KEY)
        self.model = "models/text-embedding-004"
        self.index: faiss.Index | None = None
        self.metadata: List[Dict[str, Any]] = []

    def _chunk_text(self, text: str, max_chars: int = 2000) -> List[str]:
        """Split a long text into chunks no longer than max_chars (word-boundary aware)."""
        if not text:
            return []
        words = text.split()
        chunks: List[str] = []
        current_words: List[str] = []
        current_len = 0
        for word in words:
            # +1 for space
            if current_len + len(word) + (1 if current_words else 0) > max_chars:
                if current_words:
                    chunks.append(" ".join(current_words))
                current_words = [word]
                current_len = len(word)
            else:
                current_words.append(word)
                current_len += len(word) + (1 if current_words[:-1] else 0)
        if current_words:
            chunks.append(" ".join(current_words))
        return chunks

    def create_embeddings(self, texts: List[str]) -> List[List[float]]:
        """Create embeddings for a list of texts using Gemini embeddings API."""
        embeddings: List[List[float]] = []
        for text in texts:
            result = genai.embed_content(model=self.model, content=text)
            vector = result["embedding"] if isinstance(result, dict) else result
            embeddings.append(vector)
        return embeddings

    def build_index(self, clauses: List[Dict[str, Any]]) -> None:
        """Build FAISS index from clauses (expects each clause dict to contain 'text')."""
        if not clauses:
            raise ValueError("No clauses provided for indexing")

        chunked_texts: List[str] = []
        chunked_meta: List[Dict[str, Any]] = []

        for clause in clauses:
            text = clause.get("text", "")
            if not isinstance(text, str) or not text.strip():
                continue
            chunks = self._chunk_text(text, max_chars=2000)
            for idx, chunk in enumerate(chunks):
                chunked_texts.append(chunk)
                # store per-chunk metadata retaining original fields + chunk index
                meta = {**clause}
                meta["text"] = chunk
                meta["chunk_index"] = idx
                chunked_meta.append(meta)

        if not chunked_texts:
            raise ValueError("No valid clause chunks to index")

        # Create embeddings and normalize for cosine similarity
        embeddings = self.create_embeddings(chunked_texts)
        embeddings_array = np.array(embeddings, dtype=np.float32)
        embeddings_array = _l2_normalize(embeddings_array)

        # Build FAISS index (inner product == cosine with normalized vectors)
        dimension = embeddings_array.shape[1]
        self.index = faiss.IndexFlatIP(dimension)
        self.index.add(embeddings_array)

        # Store metadata aligned by vector index
        self.metadata = chunked_meta

        # Persist to disk
        self._save_index()

    def search_index(self, query: str, top_k: int = 3) -> List[Tuple[Dict[str, Any], float]]:
        """Search FAISS index for similar clauses, return (clause_dict, score)."""
        if self.index is None:
            self._load_index()
        if self.index is None:
            raise ValueError("No index available for search")

        # Embed and normalize query
        result = genai.embed_content(model=self.model, content=query)
        query_embedding = result["embedding"] if isinstance(result, dict) else result
        query_vector = np.array([query_embedding], dtype=np.float32)
        query_vector = _l2_normalize(query_vector)

        # Search
        scores, indices = self.index.search(query_vector, top_k)

        # Collect results with metadata
        results: List[Tuple[Dict[str, Any], float]] = []
        for score, idx in zip(scores[0], indices[0]):
            if 0 <= idx < len(self.metadata):
                results.append((self.metadata[idx], float(score)))
        return results

    def _save_index(self) -> None:
        os.makedirs(os.path.dirname(Config.FAISS_INDEX_PATH), exist_ok=True)
        faiss.write_index(self.index, Config.FAISS_INDEX_PATH)
        with open(Config.METADATA_PATH, 'wb') as f:
            pickle.dump(self.metadata, f)

    def _load_index(self) -> None:
        if not os.path.exists(Config.FAISS_INDEX_PATH) or not os.path.exists(Config.METADATA_PATH):
            return
        self.index = faiss.read_index(Config.FAISS_INDEX_PATH)
        with open(Config.METADATA_PATH, 'rb') as f:
            self.metadata = pickle.load(f)

    def index_exists(self) -> bool:
        return os.path.exists(Config.FAISS_INDEX_PATH) and os.path.exists(Config.METADATA_PATH)

    def get_index_stats(self) -> Dict[str, Any]:
        if self.index is None and self.index_exists():
            self._load_index()
        if self.index is None:
            return {"index_size": 0, "dimension": 0, "metadata_size": len(self.metadata)}
        return {"index_size": self.index.ntotal, "dimension": self.index.d, "metadata_size": len(self.metadata)}
