import json
import os
from typing import Dict, List, Any, Set, Tuple
from collections import defaultdict, deque
from app.utils.config import Config


class ClauseGraphService:
    """Lightweight clause graph: nodes=clauses, edges=typed relations.

    Storage format (JSON):
    {
      "nodes": { clause_id: {"section": str|None} },
      "edges": [ {"src": id, "dst": id, "type": str, "confidence": float} ]
    }
    """

    EDGE_TYPES = {"Defines", "RefersTo", "Overrides", "Entails", "SameSection"}

    def __init__(self):
        self.nodes: Dict[str, Dict[str, Any]] = {}
        self.edges: List[Dict[str, Any]] = []
        self._adj: Dict[str, List[Tuple[str, str, float]]] = defaultdict(list)

    def build_graph(self, clauses: List[Dict[str, Any]]) -> None:
        # Add nodes
        self.nodes = {}
        self.edges = []
        self._adj = defaultdict(list)

        # Basic section inference (best-effort placeholder)
        def infer_section(text: str) -> str:
            # naive: capture leading numbering like "1.", "1.2.", or heading-like tokens
            t = text.strip().split("\n", 1)[0][:80]
            return t

        # Add all clauses as nodes
        for c in clauses:
            cid = c.get("clause_id")
            if not cid:
                continue
            self.nodes[cid] = {
                "section": c.get("section") or None
            }

        # Heuristic edge extraction
        for c in clauses:
            cid = c.get("clause_id")
            text = (c.get("original_text") or c.get("text") or "").strip()
            if not cid or not text:
                continue

            # RefersTo: find patterns like "clause 4.2" or "Section 3"
            lowered = text.lower()
            for other in clauses:
                ocid = other.get("clause_id")
                if not ocid or ocid == cid:
                    continue
                # simple heuristic: if ocid string appears in text
                if ocid.lower() in lowered:
                    self._add_edge(cid, ocid, "RefersTo", 0.7)

            # Defines: patterns like "X means" are hard without NLP; use keyword hints
            if any(kw in lowered for kw in [" shall mean ", " means ", " is defined as "]):
                # link to SameSection neighbors later; for now, self-loop as marker
                self._add_edge(cid, cid, "Defines", 0.6)

            # Overrides/Exceptions
            if any(kw in lowered for kw in ["notwithstanding", "except as provided", "subject to clause", "unless otherwise stated"]):
                # mark potential override relationship within local neighborhood
                self._add_edge(cid, cid, "Overrides", 0.6)

        # SameSection grouping (very lightweight: neighbors by proximity in list)
        for i in range(len(clauses) - 1):
            a = clauses[i].get("clause_id")
            b = clauses[i + 1].get("clause_id")
            if a and b:
                self._add_edge(a, b, "SameSection", 0.5)
                self._add_edge(b, a, "SameSection", 0.5)

    def _add_edge(self, src: str, dst: str, etype: str, conf: float) -> None:
        if etype not in self.EDGE_TYPES:
            return
        self.edges.append({"src": src, "dst": dst, "type": etype, "confidence": float(conf)})
        self._adj[src].append((dst, etype, float(conf)))

    def save(self, path: str | None = None) -> None:
        p = path or Config.CLAUSE_GRAPH_PATH
        os.makedirs(os.path.dirname(p), exist_ok=True)
        with open(p, "w", encoding="utf-8") as f:
            json.dump({"nodes": self.nodes, "edges": self.edges}, f, ensure_ascii=False, indent=2)

    def load(self, path: str | None = None) -> bool:
        p = path or Config.CLAUSE_GRAPH_PATH
        if not os.path.exists(p):
            return False
        with open(p, "r", encoding="utf-8") as f:
            data = json.load(f)
        self.nodes = data.get("nodes", {})
        self.edges = data.get("edges", [])
        self._adj = defaultdict(list)
        for e in self.edges:
            self._adj[e["src"]].append((e["dst"], e.get("type", ""), float(e.get("confidence", 0.0))))
        return True

    def expand_from_hits(self, hit_ids: List[str], k_hops: int = 1,
                          types: List[str] | None = None,
                          max_nodes: int = 20) -> List[str]:
        """Return neighbor clause_ids reachable within k hops, filtered by types, excluding hits."""
        allowed: Set[str] = set(types) if types else set(self.EDGE_TYPES)
        visited: Set[str] = set(hit_ids)
        result: List[str] = []
        q: deque[Tuple[str, int]] = deque((hid, 0) for hid in hit_ids)
        while q and len(result) < max_nodes:
            node, d = q.popleft()
            if d == k_hops:
                continue
            for (nbr, et, conf) in self._adj.get(node, []):
                if et not in allowed or conf < 0.5:
                    continue
                if nbr in visited:
                    continue
                visited.add(nbr)
                result.append(nbr)
                q.append((nbr, d + 1))
        return result

    def degree(self, cid: str) -> int:
        return len(self._adj.get(cid, []))

    def exists(self) -> bool:
        return os.path.exists(Config.CLAUSE_GRAPH_PATH)

    def get_stats(self) -> Dict[str, Any]:
        return {
            "nodes": len(self.nodes),
            "edges": len(self.edges),
            "path": Config.CLAUSE_GRAPH_PATH,
            "exists": self.exists(),
        }
