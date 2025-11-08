# Postman Testing Guide

This guide shows how to test the HackRx Clause Graph RAG API using Postman.

## 1) Start the API server
- Ensure `.env` has `GEMINI_API_KEY`
- Run: `uvicorn app.main:app --reload --port 8000`
- Base URL: `http://127.0.0.1:8000`

## 2) Health and Status checks
- GET `http://127.0.0.1:8000/api/v1/health`
- GET `http://127.0.0.1:8000/api/v1/status`
  - Response includes FAISS index and Clause Graph stats after a run.

## 3) Main endpoint: /api/v1/hackrx/run
- Method: POST
- URL: `http://127.0.0.1:8000/api/v1/hackrx/run`
- Headers:
  - `Content-Type: application/json`
  - `Accept: application/json`
  - `Authorization: Bearer <token>` (optional)
- Body (raw JSON):
```
{
  "documents": "https://hackrx.blob.core.windows.net/assets/policy.pdf?sv=2023-01-03&st=2025-07-04T09%3A11%3A24Z&se=2027-07-05T09%3A11%3A00Z&sr=b&sp=r&sig=N4a9OU0w0QXO6AOIBiu4bpl7AXvEZogeT%2FjUHNO7HzQ%3D",
  "questions": [
    "What is the grace period for premium payment?",
    "Does this policy cover maternity expenses?"
  ]
}
```
- Click Send. On the first run, the service will:
  - Download and parse the policy document
  - Extract clauses, embed, build FAISS index
  - Build and save the Clause Graph
  - Retrieve + generate answers

### Toggle Vanilla vs CG-RAG via header
- Add header `X-Use-Graph: false` to run Vanilla RAG (FAISS-only, no graph expansion).
- Add header `X-Use-Graph: true` to run CG-RAG (default if header omitted).

## 4) Inspecting results
- A successful response returns:
```
{
  "answers": [
    "A grace period of thirty days is provided ...",
    "Yes, the policy covers maternity expenses ..."
  ]
}
```
- Check `/api/v1/status` after a successful run:
  - `index_status.index_stats.index_size > 0`
  - `graph.nodes > 0`, `graph.edges > 0`

## 5) Optional: Testing Vanilla vs CG-RAG
- Current default is CG-RAG (graph-aware retrieval).
- Preferred: use the `X-Use-Graph` header to toggle.
- Alternative: remove `data/clause_graph.json` to force Vanilla fallback.

## 6) Troubleshooting
- 400 error: likely no clauses extracted or invalid document URL.
- 500 error: ensure `GEMINI_API_KEY` is valid and network access is available.
- Large PDFs can take longer on first run; retries will reuse the index/graph from `data/`.
