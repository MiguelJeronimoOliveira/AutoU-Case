"""Custom exceptions for the application."""

from fastapi import HTTPException, status


class EmailClassificationError(HTTPException):
    """Base exception for email classification errors."""
    
    def __init__(self, detail: str, status_code: int = status.HTTP_500_INTERNAL_SERVER_ERROR):
        super().__init__(status_code=status_code, detail=detail)


class ModelLoadError(EmailClassificationError):
    """Exception raised when model fails to load."""
    
    def __init__(self, detail: str = "Erro ao carregar modelo"):
        super().__init__(detail=detail, status_code=status.HTTP_503_SERVICE_UNAVAILABLE)


class FileProcessingError(EmailClassificationError):
    """Exception raised when file processing fails."""
    
    def __init__(self, detail: str = "Erro ao processar arquivo"):
        super().__init__(detail=detail, status_code=status.HTTP_400_BAD_REQUEST)


class RAGError(EmailClassificationError):
    """Exception raised when RAG operations fail."""
    
    def __init__(self, detail: str = "Erro na operação RAG"):
        super().__init__(detail=detail, status_code=status.HTTP_503_SERVICE_UNAVAILABLE)

