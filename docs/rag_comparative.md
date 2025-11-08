# Comparative Study: Vanilla RAG vs Clause Graph-Enhanced RAG (CG-RAG)

## Overview
This document contrasts standard Retrieval-Augmented Generation (RAG) with Clause Graph-Enhanced RAG (CG-RAG), focusing on retrieval relevance, reasoning, coherence, latency, and evaluation methodology.

## Datasets Used (for prototype evaluation)
- HackRx policy sample (document referenced in `test_api_improved.py`) with ~10 author-written questions.
- Small public QA subsets (~50 items) adapted from HotpotQA and 2WikiMultihopQA to mimic clause-style retrieval and multi-hop reasoning.
 - In-domain PDFs under `docs/dataset/` used for batch evaluation via `scripts/batch_evaluate.py`.

## 1. Architectures
- **Vanilla RAG**
  - Passage/Clause embeddings → FAISS top-k → prompt → LLM answer
  - Optional: BM25 hybrid, cross-encoder re-rank
- **CG-RAG (Ours)**
  - Clause extraction → embeddings → FAISS top-k
  - Clause Graph build (nodes: clauses; edges: Defines, RefersTo, Overrides, Entails, SameSection)
  - Graph expansion (k-hop) + reranking (sim + graph features)
  - Graph-aware prompting with reasoning paths

## 2. How Differences Arise
- **Structured Context Completion**: Graph expansion pulls in definitions/exceptions referenced by top-k.
- **Conflict Handling**: Overrides edges surface limitations that prevent contradictions.
- **Explainability**: Reasoning paths (edge trails) guide the LLM to faithful answers.
- **Robustness to Chunking**: SameSection/RefersTo edges link split content.

## 3. Pros and Cons
- **Vanilla RAG Pros**
  - Simpler, fast, fewer moving parts
  - Strong on lexical/semantic similarity
- **Vanilla RAG Cons**
  - Misses multi-hop dependencies, definitions, exceptions
  - Higher hallucination/contradiction risk
  - Sensitive to chunking boundaries

- **CG-RAG Pros**
  - Higher recall of governing clauses (definitions/exceptions)
  - Lower contradiction rate, better faithfulness
  - More interpretable via paths
- **CG-RAG Cons**
  - Extra compute and engineering for graph build and traversal
  - Edge extraction noise can hurt if unfiltered; requires thresholds
  - Slight latency overhead during retrieval

## 4. Quantitative/Analytical Comparison Methods
- **Retrieval**: Recall@k, nDCG@k, MRR using gold clause sets.
- **Generation**: EM/F1 (if QA set), ROUGE-L/BLEU, Faithfulness (NLI-based or RAGAS), Contradiction rate.
- **Ablations**: No-graph vs graph; k-hop depth; edge-type filters; scoring weights.
- **Latency**: p50/p95 end-to-end latency; breakdown by stage.

## 5. Minimal Pseudocode Differences

Vanilla RAG:
```python
hits = dense_retrieve(I, q, top_k=8)
context = concat([c.text for c,_ in hits])
answer = LLM.generate(prompt(q, context))
```

CG-RAG:
```python
hits = dense_retrieve(I, q, top_k=5)
neighbors = expand_graph(G, ids(hits), k=1, types=['Defines','Overrides','RefersTo'])
pool = dedupe(hits + neighbors)
reranked = rerank(pool, score=lambda x: 0.7*x.sim + 0.3*x.graph)
context = structure_by_role(reranked[:8])
answer = LLM.generate(prompt_graph(q, context, cite_edges=True))
```

## 6. Expected Outcomes
- +5–15% Recall@5 on clause retrieval in policy/legal QA.
- −20–40% contradiction rate vs. Vanilla.
- Comparable or slightly higher latency (+10–25%).
- Stronger qualitative coherence in case studies.

## 7. Sample Results (illustrative)

| Metric (avg)       | Vanilla RAG | CG-RAG |
|--------------------|-------------|--------|
| Recall@5 (clauses) | 0.62        | 0.74   |
| nDCG@5             | 0.55        | 0.68   |
| Faithfulness (↑)   | 0.71        | 0.82   |
| Contradiction (↓)  | 0.18        | 0.09   |
| Latency p50 (s)    | 2.1         | 2.6    |

ASCII (Recall@5):

Vanilla: ##############........ (0.62)
CG-RAG : ##################.... (0.74)

## 8. Artifacts from Prototype Run
- CSV: `docs/eval_metrics.csv` (per-document latency and basic stats)
- Plot: `docs/plots/latency_bar.png` (average latency comparison)

Note: For broader benchmarking, future work will compare against public datasets like PrivacyGLUE (privacy policy NLP) and include standard encoders (e.g., BERT) as reference baselines for retrieval quality.

## 7. Recommendations
- Start with heuristic edges; add LLM-assisted extraction after.
- Keep k-hop=1 for latency; filter edges by confidence ≥0.6.
- Log edge paths included in each answer for auditability.
