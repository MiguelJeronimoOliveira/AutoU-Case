"""Email analysis endpoints."""

from fastapi import APIRouter, Depends, File, UploadFile

from app.api.deps import get_classifier, get_file_processor, get_response_generator
from app.handlers import EmailAnalysisHandler
from app.models import EmailRequest, EmailResponse

router = APIRouter()


@router.post("/analyze", response_model=EmailResponse, tags=["email"])
async def analyze_email(
    request: EmailRequest,
    classifier=Depends(get_classifier),
    response_generator=Depends(get_response_generator),
    file_processor=Depends(get_file_processor)
) -> EmailResponse:
    """Analyze email content or file path."""
    email_handler = EmailAnalysisHandler(classifier, response_generator, file_processor)
    return email_handler.handle_analyze_email(request)


@router.post("/analyze/upload", response_model=EmailResponse, tags=["email"])
async def analyze_uploaded_email(
    file: UploadFile = File(...),
    classifier=Depends(get_classifier),
    response_generator=Depends(get_response_generator),
    file_processor=Depends(get_file_processor)
) -> EmailResponse:
    """Analyze uploaded email file."""
    email_handler = EmailAnalysisHandler(classifier, response_generator, file_processor)
    return await email_handler.handle_analyze_upload(file)

