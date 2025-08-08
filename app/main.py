from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.hackrx import router as hackrx_router
from app.utils.config import Config

# Initialize FastAPI app
app = FastAPI(
    title="HackRx 6.0 - LLM-powered Clause Retrieval System (Gemini)",
    description="Retrieve relevant clauses from insurance policy documents using Gemini embeddings and FAISS.",
    version="1.1.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers with /api/v1 prefix
app.include_router(hackrx_router, prefix="/api/v1", tags=["hackrx"])

@app.on_event("startup")
async def startup_event():
    try:
        Config.validate()
        print("✅ Configuration validated successfully")
        print("🚀 HackRx 6.0 Clause Retrieval System (Gemini) started")
    except Exception as e:
        print(f"❌ Configuration validation failed: {str(e)}")
        print("Please check your .env file and ensure GEMINI_API_KEY is set")

@app.get("/")
async def root():
    return {
        "message": "HackRx 6.0 - LLM-powered Clause Retrieval System (Gemini)",
        "version": "1.1.0",
        "endpoints": {
            "main": "/api/v1/hackrx/run",
            "health": "/api/v1/health",
            "status": "/api/v1/status",
            "docs": "/docs"
        }
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
