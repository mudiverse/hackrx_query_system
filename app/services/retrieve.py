from typing import List, Dict, Any
import google.generativeai as genai
from app.services.embed import EmbeddingService
from app.utils.config import Config


class RetrievalService:
    """Service for retrieving relevant clauses and generating answers via Gemini."""

    def __init__(self):
        self.embedding_service = EmbeddingService()
        self.config = Config()
        genai.configure(api_key=self.config.GEMINI_API_KEY)
        self.gen_model = genai.GenerativeModel(self.config.GEMINI_GEN_MODEL)

    def _generate_answer(self, question: str, clauses: List[Dict[str, Any]]) -> str:
        if not clauses:
            return "No relevant information found in the policy document."

        context = "\n\n".join([f"Clause {i+1}: {c['text']}" for i, c in enumerate(clauses)])
        prompt = (
            "You are a helpful assistant for insurance policy Q&A in India. "
            "Answer the user's question using ONLY the provided policy clauses. "
            "If the answer is not in the clauses, say you cannot find it in the policy. "
            "Be concise and quote exact phrasing when possible.\n\n"
            f"Question: {question}\n\n"
            f"Policy Clauses:\n{context}\n\n"
            "Answer:"
        )
        try:
            resp = self.gen_model.generate_content(prompt)
            return resp.text.strip() if hasattr(resp, 'text') and resp.text else ""
        except Exception:
            # Fallback: return the best clause text
            return clauses[0]["text"]

    def answer_question(self, question: str) -> str:
        try:
            results = self.embedding_service.search_index(question, top_k=3)
            top_clauses = [c for (c, _s) in results]
            return self._generate_answer(question, top_clauses)
        except Exception as e:
            return f"Error retrieving answer: {str(e)}"

    def answer_questions(self, questions: List[str]) -> List[str]:
        return [self.answer_question(q) for q in questions]

    def get_relevant_clauses(self, question: str, top_k: int = 3) -> List[Dict[str, Any]]:
        try:
            results = self.embedding_service.search_index(question, top_k=top_k)
            clauses_with_scores: List[Dict[str, Any]] = []
            for clause, score in results:
                c = clause.copy()
                c["similarity_score"] = score
                clauses_with_scores.append(c)
            return clauses_with_scores
        except Exception:
            return []

    def check_index_status(self) -> Dict[str, Any]:
        try:
            stats = self.embedding_service.get_index_stats()
            exists = self.embedding_service.index_exists()
            return {"index_exists": exists, "index_stats": stats, "ready_for_queries": exists and stats.get("index_size", 0) > 0}
        except Exception as e:
            return {"index_exists": False, "index_stats": {"index_size": 0, "dimension": 0}, "ready_for_queries": False, "error": str(e)}
