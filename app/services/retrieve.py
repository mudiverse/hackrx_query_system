from typing import List, Dict, Any
import google.generativeai as genai
from app.services.embed import EmbeddingService
from app.utils.config import Config
from app.services.clause_graph import ClauseGraphService


class RetrievalService:
    """Service for retrieving relevant clauses and generating answers via Gemini."""

    def __init__(self):
        self.embedding_service = EmbeddingService()
        self.config = Config()
        genai.configure(api_key=self.config.GEMINI_API_KEY)
        self.gen_model = genai.GenerativeModel(self.config.GEMINI_GEN_MODEL)
        # Graph service (optional if not built yet)
        self.graph_service = ClauseGraphService()
        self.graph_service.load()

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

    def _graph_expand_and_rerank(self, question: str, hits: List[Any], top_k: int = 5) -> List[Dict[str, Any]]:
        """Expand FAISS hits via clause graph neighbors and rerank by combined score.

        hits: List of tuples (clause_dict, sim_score)
        returns: top clauses (dicts)
        """
        # Map of clause_id -> (clause_dict, sim)
        hit_map: Dict[str, Any] = {}
        for clause, sim in hits:
            cid = clause.get("clause_id")
            if cid:
                hit_map[cid] = (clause, float(sim))

        hit_ids = list(hit_map.keys())

        # If graph not available, return top by sim only
        if not self.graph_service.exists():
            return [c for (c, _s) in hits[:top_k]]

        # Expand one hop around hits focusing on key relations
        neighbor_ids = self.graph_service.expand_from_hits(
            hit_ids, k_hops=1, types=["Defines", "Overrides", "RefersTo"], max_nodes=20
        )

        # Gather neighbor clause dicts from metadata (linear scan acceptable for small sets)
        neighbor_entries: Dict[str, Dict[str, Any]] = {}
        for nid in neighbor_ids:
            if nid in hit_map:
                continue
            for meta in self.embedding_service.metadata:
                if meta.get("clause_id") == nid:
                    neighbor_entries[nid] = meta
                    break

        # Build scoring pool
        scored: List[Dict[str, Any]] = []
        # include hits with sim.
        for cid, (clause, sim) in hit_map.items():
            graph_boost = self.graph_service.degree(cid)
            score = 0.7 * sim + 0.3 * graph_boost
            scored.append({"clause": clause, "score": score})
        # include neighbors with zero sim but graph boost
        for cid, clause in neighbor_entries.items():
            graph_boost = self.graph_service.degree(cid)
            score = 0.3 * graph_boost
            scored.append({"clause": clause, "score": score})

        scored.sort(key=lambda x: x["score"], reverse=True)
        return [x["clause"] for x in scored[:top_k]]

    def answer_question(self, question: str, use_graph: bool = True) -> str:
        try:
            results = self.embedding_service.search_index(question, top_k=5)
            if use_graph and self.graph_service.exists():
                top_clauses = self._graph_expand_and_rerank(question, results, top_k=6)
            else:
                top_clauses = [c for (c, _s) in results][:6]
            return self._generate_answer(question, top_clauses)
        except Exception as e:
            return f"Error retrieving answer: {str(e)}"

    def answer_questions(self, questions: List[str], use_graph: bool = True) -> List[str]:
        return [self.answer_question(q, use_graph=use_graph) for q in questions]

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
