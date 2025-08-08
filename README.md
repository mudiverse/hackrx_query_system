# HackRx 6.0 - LLM-powered Clause Retrieval System (Gemini)

A FastAPI-based system for retrieving relevant clauses from insurance policy documents using Google Gemini embeddings, FAISS search, and Gemini text generation. Built for the HackRx 6.0 hackathon.

## 🎯 Features

- Document Processing: Extract text from PDF and DOCX policy documents
- Clause Extraction: Tuned parser for Indian insurance policies (including Arogya Sanjeevani Policy)
- Embeddings: Google Gemini (`models/text-embedding-004`) for semantic search
- FAISS Index: Local vector storage for fast similarity search
- Question Answering: Retrieve relevant clauses and generate answers using Gemini (`gemini-1.5-flash`)

## 📂 Project Structure

```
hackrx_query_system/
├── app/
│   ├── main.py                # FastAPI entrypoint
│   ├── api/
│   │   └── hackrx.py          # /hackrx/run endpoint
│   ├── services/
│   │   ├── ingest.py          # Document parsing & clause extraction
│   │   ├── embed.py           # Gemini embeddings + FAISS index
│   │   └── retrieve.py        # FAISS search & Gemini answer generation
│   └── utils/
│       ├── config.py          # Environment configuration
│       └── text_utils.py      # Text cleaning utilities
├── data/                      # FAISS index + clause storage
├── requirements.txt
└── README.md
```

## 🚀 Quick Start

1) Install dependencies
```bash
pip install -r requirements.txt
```

2) Set up environment
Create a `.env` file in the project root:
```env
GEMINI_API_KEY=your-gemini-api-key
```

3) Run the application
```bash
uvicorn app.main:app --reload --port 8000
```

## 📚 API

### Main Endpoint: `/hackrx/run`
Method: POST

Headers:
- Content-Type: application/json
- Accept: application/json
- Authorization: Bearer <team_token> (optional, accepted)

Request Body:
```json
{
  "documents": "https://example.com/policy-document.pdf",
  "questions": [
    "What is the grace period for premium payment?",
    "Does this policy cover maternity expenses?"
  ]
}
```

Response Body:
```json
{
  "answers": [
    "A grace period of thirty days is provided ...",
    "Yes, the policy covers maternity expenses ..."
  ]
}
```

## 🧠 How It Works

1. Ingestion: Downloads document, extracts text (PyMuPDF for PDF, python-docx for DOCX), cleans headers/footers, splits into clauses
2. Embedding & Indexing: Creates Gemini embeddings for each clause, normalizes vectors, stores in FAISS
3. Retrieval & Generation: For each question, retrieves top clauses and uses Gemini to generate a concise answer grounded in the clauses

## 🔧 Configuration
- GEMINI_API_KEY from `.env`
- Embedding model: `models/text-embedding-004`
- Generation model: `gemini-1.5-flash`
- FAISS index: `data/faiss_index.bin`
- Metadata: `data/metadata.pkl`
- Clauses: `data/clauses.json`

## Testing
Use the included Python/PowerShell scripts or curl as before. Endpoint is now at `/hackrx/run`.
