from typing import List
from fastapi import APIRouter, HTTPException, Depends, Header
from pydantic import BaseModel
from app.services.ingest import DocumentIngestionService
from app.services.embed import EmbeddingService
from app.services.retrieve import RetrievalService
from app.utils.config import Config

router = APIRouter()

class HackRxRequest(BaseModel):
    documents: str
    questions: List[str]

class HackRxResponse(BaseModel):
    answers: List[str]

def get_services():
    """Dependency to get service instances."""
    return {
        "ingest": DocumentIngestionService(),
        "embed": EmbeddingService(),
        "retrieve": RetrievalService()
    }

@router.post("/hackrx/run", response_model=HackRxResponse)
async def run_hackrx_query(
    request: HackRxRequest,
    services: dict = Depends(get_services),
    authorization: str = Header(None, alias="Authorization")
):
    """
    Main endpoint for HackRx 6.0 clause retrieval system.
    
    Processes a policy document and answers questions using LLM-powered retrieval.
    """
    try:
        # Validate configuration
        Config.validate()
        
        ingest_service = services["ingest"]
        embed_service = services["embed"]
        retrieve_service = services["retrieve"]
        
        # Step 1: Process document and extract clauses
        print(f"Processing document: {request.documents}")
        clauses = ingest_service.process_document(request.documents)
        
        if not clauses:
            raise HTTPException(
                status_code=400, 
                detail="No clauses extracted from document. Please check the document URL."
            )
        
        print(f"Extracted {len(clauses)} clauses from document")
        
        # Step 2: Build FAISS index from clauses
        print("Building FAISS index...")
        embed_service.build_index(clauses)
        
        index_stats = embed_service.get_index_stats()
        print(f"Index built successfully: {index_stats['index_size']} vectors, {index_stats['dimension']} dimensions")
        
        # Step 3: Answer questions using retrieval
        print(f"Answering {len(request.questions)} questions...")
        answers = retrieve_service.answer_questions(request.questions)
        
        print("Query processing completed successfully")
        
        return HackRxResponse(answers=answers)
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        print(f"Error in /hackrx/run: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@router.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "service": "HackRx Clause Retrieval System"}

@router.get("/status")
async def get_status(services: dict = Depends(get_services)):
    """Get system status including index information."""
    try:
        retrieve_service = services["retrieve"]
        status = retrieve_service.check_index_status()
        
        return {
            "status": "operational",
            "index_status": status,
            "ready_for_queries": status["ready_for_queries"]
        }
    except Exception as e:
        return {
            "status": "error",
            "error": str(e),
            "ready_for_queries": False
        }
