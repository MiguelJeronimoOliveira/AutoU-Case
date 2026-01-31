"""Request handlers for email classification API endpoints."""

import logging
import os
import tempfile
from typing import Optional

from fastapi import HTTPException, UploadFile

from app.classifier import EmailClassifier
from app.core.constants import CONTENT_PREVIEW_LENGTH, SUPPORTED_FILE_EXTENSIONS
from app.file_processor import FileProcessor
from app.models import EmailAnalysis, EmailCategory, EmailRequest, EmailResponse
from app.response_generator import ResponseGenerator
from app.rag_retriever import RAGRetriever

logger = logging.getLogger(__name__)


class EmailAnalysisHandler:
    def __init__(
        self,
        classifier: EmailClassifier,
        response_generator: ResponseGenerator,
        file_processor: FileProcessor
    ):
        self.classifier = classifier
        self.response_generator = response_generator
        self.file_processor = file_processor

    #validate file extension against supported types
    #@param file_extension: file extension to validate
    #@return: None
    def validate_file_extension(self, file_extension: str) -> None:
        if file_extension not in SUPPORTED_FILE_EXTENSIONS:
            raise HTTPException(
                status_code=400,
                detail=(
                    f"Unsupported file type: {file_extension}. "
                    f"Supported types: {', '.join(SUPPORTED_FILE_EXTENSIONS)}"
                )
            )

    #process email content and generate analysis
    #@param email_content: content of the email to analyze
    #@return: EmailAnalysis object with classification and response
    def process_email_analysis(self, email_content: str) -> EmailAnalysis:
        try:
            category, confidence, reasoning = self.classifier.classify_email(email_content)
            
            suggested_response = self.response_generator.generate_response(
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

    #handle email analysis request
    #@param request: email request with file_path or email_content
    #@return: EmailResponse with analysis results
    def handle_analyze_email(self, request: EmailRequest) -> EmailResponse:
        try:
            if request.file_path:
                email_content = self.file_processor.process_file(request.file_path)
            elif request.email_content:
                email_content = request.email_content
            else:
                raise HTTPException(
                    status_code=400,
                    detail="Either 'file_path' or 'email_content' must be provided"
                )
            
            analysis = self.process_email_analysis(email_content)
            
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

    #handle uploaded file analysis
    #@param file: uploaded file to analyze
    #@return: EmailResponse with analysis results
    async def handle_analyze_upload(self, file: UploadFile) -> EmailResponse:
        if not file.filename:
            raise HTTPException(
                status_code=400,
                detail="Filename is required"
            )
        
        file_extension = os.path.splitext(file.filename)[1].lower()
        self.validate_file_extension(file_extension)
        
        temp_path = None
        try:
            with tempfile.NamedTemporaryFile(
                delete=False,
                suffix=file_extension
            ) as temp_file:
                content = await file.read()
                temp_file.write(content)
                temp_path = temp_file.name
            
            email_content = self.file_processor.process_file(temp_path)
            
            analysis = self.process_email_analysis(email_content)
            
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
            if temp_path and os.path.exists(temp_path):
                try:
                    os.unlink(temp_path)
                except OSError as e:
                    logger.warning(f"Failed to delete temporary file {temp_path}: {str(e)}")


class HealthHandler:
    def __init__(
        self,
        response_generator: ResponseGenerator,
        rag_retriever: Optional[RAGRetriever] = None
    ):
        self.response_generator = response_generator
        self.rag_retriever = rag_retriever

    #get health check information
    #@return: dictionary with health status
    def get_health_info(self) -> dict:
        health_info = {
            "status": "healthy",
            "classifier": "loaded",
            "response_generator": "loaded",
            "rag_enabled": self.response_generator.use_rag if self.response_generator else False
        }
        
        if self.rag_retriever:
            try:
                rag_stats = self.rag_retriever.get_collection_stats()
                health_info["rag"] = rag_stats
            except Exception as e:
                health_info["rag"] = {"status": "error", "error": str(e)}
        
        return health_info


class RAGHandler:
    def __init__(self, rag_retriever: Optional[RAGRetriever] = None):
        self.rag_retriever = rag_retriever

    #check if RAG retriever is available
    #@return: None
    def _check_rag_available(self) -> None:
        if not self.rag_retriever:
            raise HTTPException(
                status_code=503,
                detail="RAG Retriever não está disponível"
            )

    #get RAG collection statistics
    #@return: dictionary with statistics
    def get_rag_stats(self) -> dict:
        self._check_rag_available()
        
        try:
            stats = self.rag_retriever.get_collection_stats()
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

    #get RAG documents with optional filtering
    #@param limit: maximum number of documents to return
    #@param category: optional category filter
    #@param full: whether to include full document content
    #@return: dictionary with documents
    def get_rag_documents(
        self,
        limit: int,
        category: Optional[str],
        full: bool
    ) -> dict:
        self._check_rag_available()
        
        try:
            category_enum = None
            if category:
                if category not in ["productive", "unproductive"]:
                    raise HTTPException(
                        status_code=400,
                        detail="Categoria deve ser 'productive' ou 'unproductive'"
                    )
                category_enum = EmailCategory.PRODUCTIVE if category == "productive" else EmailCategory.UNPRODUCTIVE
            
            documents = self.rag_retriever.get_all_documents(limit=limit, category=category_enum)
            
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

    #clear RAG history
    #@return: dictionary with deletion results
    def clear_rag_history(self) -> dict:
        self._check_rag_available()
        
        try:
            deleted_count = self.rag_retriever.clear_history()
            return {
                "success": True,
                "message": f"Histórico limpo com sucesso. {deleted_count} documentos removidos.",
                "deleted_count": deleted_count
            }
        except Exception as e:
            logger.error(f"Erro ao limpar histórico RAG: {str(e)}")
            raise HTTPException(
                status_code=500,
                detail=f"Erro ao limpar histórico: {str(e)}"
            )

