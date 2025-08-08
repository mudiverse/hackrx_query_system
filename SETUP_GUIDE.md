# HackRx 6.0 Setup Guide

## 🚀 Quick Setup

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Create Environment File
Create a `.env` file in the project root:
```env
OPENAI_API_KEY=sk-your-openai-api-key-here
```

### 3. Run the Server
```bash
uvicorn app.main:app --reload --port 8000
```

## 🧪 Testing Options

### Option 1: Python Script (Recommended)
```bash
python test_api_improved.py
```

### Option 2: PowerShell Script
```powershell
.\test_api.ps1
```

### Option 3: Windows Batch File
```cmd
test_curl_windows.bat
```

### Option 4: Manual curl (Windows)
```cmd
curl -X POST "http://127.0.0.1:8000/api/v1/hackrx/run" -H "Content-Type: application/json" -H "Authorization: Bearer 273418978cb9f079f5da0cd221de3a8c4ae3d5a9b29477367d3e51c2f3763444" -d "{\"documents\": \"https://hackrx.blob.core.windows.net/assets/policy.pdf?sv=2023-01-03^&st=2025-07-04T09%%3A11%%3A24Z^&se=2027-07-05T09%%3A11%%00Z^&sr=b^&sp=r^&sig=N4a9OU0w0QXO6AOIBiu4bpl7AXvEZogeT%%2FjUHNO7HzQ%%3D\", \"questions\": [\"What is the grace period for premium payment under the National Parivar Mediclaim Plus Policy?\",\"Does this policy cover maternity expenses?\"]}"
```

### Option 5: Manual curl (Linux/Mac)
```bash
curl -X POST "http://127.0.0.1:8000/api/v1/hackrx/run" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer 273418978cb9f079f5da0cd221de3a8c4ae3d5a9b29477367d3e51c2f3763444" \
  -d '{
    "documents": "https://hackrx.blob.core.windows.net/assets/policy.pdf?sv=2023-01-03&st=2025-07-04T09%3A11%3A24Z&se=2027-07-05T09%3A11%3A00Z&sr=b&sp=r&sig=N4a9OU0w0QXO6AOIBiu4bpl7AXvEZogeT%2FjUHNO7HzQ%3D",
    "questions": [
      "What is the grace period for premium payment under the National Parivar Mediclaim Plus Policy?",
      "Does this policy cover maternity expenses?"
    ]
  }'
```

## 📊 API Endpoints

- **Main API**: `POST /api/v1/hackrx/run`
- **Health Check**: `GET /api/v1/health`
- **Status**: `GET /api/v1/status`
- **Documentation**: `GET /docs`

## 🔧 Troubleshooting

### Common Issues:

1. **JSON parsing error**: Use the Python script instead of curl
2. **Authorization header**: Make sure to include the Bearer token
3. **OpenAI API key**: Ensure your `.env` file has the correct API key
4. **Port conflicts**: Change port if 8000 is busy: `--port 8001`

### Expected Response:
```json
{
  "answers": [
    "Grace period information from the policy...",
    "Maternity coverage details from the policy..."
  ]
}
```

## 🎯 HackRx 6.0 Compliance

✅ **Endpoint**: `/api/v1/hackrx/run`  
✅ **Method**: POST  
✅ **Headers**: Content-Type, Authorization  
✅ **Request**: Document URL + Questions array  
✅ **Response**: Answers array  
✅ **Document Processing**: PDF/DOCX support  
✅ **Embeddings**: OpenAI text-embedding-ada-002  
✅ **Search**: FAISS index with cosine similarity  
✅ **Storage**: Local data/ directory  

The system is fully compliant with HackRx 6.0 requirements!
