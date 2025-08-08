# HackRx 6.0 Setup Guide

## 🚀 Quick Setup (Local)

### 1. Create and activate a virtualenv
```bash
python -m venv venv
# macOS/Linux
source venv/bin/activate
# Windows
venv\Scripts\activate
```

### 2. Install dependencies
```bash
pip install --upgrade pip
pip install -r requirements.txt
```

### 3. Create Environment File
Create a `.env` file in the project root:
```env
GEMINI_API_KEY=sk-your-gemini-api-key
```

### 4. Run the Server
```bash
uvicorn main:app --reload --port 8000
```

## 🧪 Testing Options

- Python: `python test_api_improved.py`
- PowerShell: `./test_api.ps1`
- curl (Windows): `test_curl_windows.bat`

## 🧰 Render Deployment Notes

- This repo includes:
  - `requirements.txt` with pinned, wheel-only dependencies
  - `runtime.txt` with `python-3.11.9`
  - `Procfile` using `web: uvicorn main:app --host 0.0.0.0 --port $PORT`
- Avoid Rust builds; we do not pin pydantic_core explicitly and rely on wheels.
- App is lightweight at startup and loads external services lazily.

## 📚 API
- POST `/api/v1/hackrx/run`
- GET `/api/v1/health`
- GET `/api/v1/status`
