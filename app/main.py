"""Main FastAPI application for email classification API."""

import logging
import os
import tempfile
from typing import Optional, Tuple

from fastapi import FastAPI, HTTPException, UploadFile, File, Query
from fastapi.middleware.cors import CORSMiddleware

from app.classifier import EmailClassifier
from app.file_processor import FileProcessor
from app.models import EmailAnalysis, EmailRequest, EmailResponse
from app.response_generator import ResponseGenerator
from app.rag_retriever import RAGRetriever

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

SUPPORTED_FILE_EXTENSIONS = [".txt", ".pdf"]
CONTENT_PREVIEW_LENGTH = 500
UVICORN_HOST = "0.0.0.0"
UVICORN_PORT = 8000

app = FastAPI()

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize components
classifier = EmailClassifier()
response_generator = ResponseGenerator()
file_processor = FileProcessor()

# Initialize RAG Retriever (if available)
rag_retriever = None
try:
    if response_generator.use_rag and response_generator.rag_retriever:
        rag_retriever = response_generator.rag_retriever
        logger.info("RAG Retriever disponível na API")
except Exception as e:
    logger.warning(f"RAG Retriever não disponível: {str(e)}")


def _validate_file_extension(file_extension: str) -> None:
    if file_extension not in SUPPORTED_FILE_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail=(
                f"Unsupported file type: {file_extension}. "
                f"Supported types: {', '.join(SUPPORTED_FILE_EXTENSIONS)}"
            )
        )


def _process_email_analysis(email_content: str) -> EmailAnalysis:
    try:
        # Classify email
        category, confidence, reasoning = classifier.classify_email(email_content)
        
        suggested_response = response_generator.generate_response(
            email_content, category
        )
        
        return EmailAnalysis(
            content=email_content[:CONTENT_PREVIEW_LENGTH],
            full_content=email_content,
            category=category,
            confidence=confidence,
            suggested_response=suggested_response,
            reasoning=reasoning
        )
    except Exception as e:
        logger.error(f"Error processing email analysis: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Error processing email analysis: {str(e)}"
        )


@app.get("/health")
async def health_check() -> dict:
    health_info = {
        "status": "healthy",
        "classifier": "loaded",
        "response_generator": "loaded",
        "rag_enabled": response_generator.use_rag if response_generator else False
    }
    
    # Adicionar estatísticas RAG se disponível
    if rag_retriever:
        try:
            rag_stats = rag_retriever.get_collection_stats()
            health_info["rag"] = rag_stats
        except Exception as e:
            health_info["rag"] = {"status": "error", "error": str(e)}
    
    return health_info


@app.get("/rag/stats")
async def get_rag_stats() -> dict:
    """Retorna estatísticas da base de conhecimento RAG."""
    if not rag_retriever:
        raise HTTPException(
            status_code=503,
            detail="RAG Retriever não está disponível"
        )
    
    try:
        stats = rag_retriever.get_collection_stats()
        return {
            "success": True,
            "stats": stats
        }
    except Exception as e:
        logger.error(f"Erro ao obter estatísticas RAG: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Erro ao obter estatísticas: {str(e)}"
        )

#
@app.get("/rag/documents")
async def get_rag_documents(
    limit: int = Query(50, ge=1, le=500),
    category: Optional[str] = Query(None, regex="^(productive|unproductive)$"),
    full: bool = Query(False)
) -> dict:

    if not rag_retriever:
        raise HTTPException(
            status_code=503,
            detail="RAG Retriever não está disponível"
        )
    
    try:
        from app.models import EmailCategory
        
        category_enum = None
        if category:
            if category not in ["productive", "unproductive"]:
                raise HTTPException(
                    status_code=400,
                    detail="Categoria deve ser 'productive' ou 'unproductive'"
                )
            category_enum = EmailCategory.PRODUCTIVE if category == "productive" else EmailCategory.UNPRODUCTIVE
        
        documents = rag_retriever.get_all_documents(limit=limit, category=category_enum)
        
        # format documents for response
        formatted_docs = []
        for doc in documents:
            metadata = doc["metadata"]
            formatted_doc = {
                "id": doc["id"],
                "category": metadata.get("category", "unknown"),
                "created_at": metadata.get("created_at", "unknown"),
                "email_content": metadata.get("email_content", ""),
                "response": metadata.get("response", "")
            }
            
            if full:
                formatted_doc["full_document"] = doc["document"]
            
            formatted_docs.append(formatted_doc)
        
        return {
            "success": True,
            "count": len(formatted_docs),
            "limit": limit,
            "category_filter": category,
            "documents": formatted_docs
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro ao obter documentos RAG: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Erro ao obter documentos: {str(e)}"
        )


@app.post("/analyze", response_model=EmailResponse)
async def analyze_email(request: EmailRequest) -> EmailResponse:
    try:
        # Get email content
        if request.file_path:
            email_content = file_processor.process_file(request.file_path)
        elif request.email_content:
            email_content = request.email_content
        else:
            raise HTTPException(
                status_code=400,
                detail="Either 'file_path' or 'email_content' must be provided"
            )
        
        analysis = _process_email_analysis(email_content)
        
        return EmailResponse(
            success=True,
            analysis=analysis,
            error=None
        )
    
    except HTTPException:
        raise
    except FileNotFoundError as e:
        logger.error(f"File not found: {str(e)}")
        raise HTTPException(status_code=404, detail=str(e))
    except ValueError as e:
        logger.error(f"Validation error: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Unexpected error in analyze_email: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Internal server error: {str(e)}"
        )


@app.post("/analyze/upload", response_model=EmailResponse)
async def analyze_uploaded_email(file: UploadFile = File(...)) -> EmailResponse:
    if not file.filename:
        raise HTTPException(
            status_code=400,
            detail="Filename is required"
        )
    
    # Validate file type
    file_extension = os.path.splitext(file.filename)[1].lower()
    _validate_file_extension(file_extension)
    
    temp_path = None
    try:
        # Save uploaded file temporarily
        with tempfile.NamedTemporaryFile(
            delete=False,
            suffix=file_extension
        ) as temp_file:
            content = await file.read()
            temp_file.write(content)
            temp_path = temp_file.name
        
        email_content = file_processor.process_file(temp_path)
        
        analysis = _process_email_analysis(email_content)
        
        return EmailResponse(
            success=True,
            analysis=analysis,
            error=None
        )
    
    except HTTPException:
        raise
    except FileNotFoundError as e:
        logger.error(f"File not found: {str(e)}")
        raise HTTPException(status_code=404, detail=str(e))
    except ValueError as e:
        logger.error(f"Validation error: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Unexpected error in analyze_uploaded_email: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Internal server error: {str(e)}"
        )
    finally:
        # Clean up temporary file
        if temp_path and os.path.exists(temp_path):
            try:
                os.unlink(temp_path)
            except OSError as e:
                logger.warning(f"Failed to delete temporary file {temp_path}: {str(e)}")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host=UVICORN_HOST, port=UVICORN_PORT)

