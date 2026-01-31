"""Email flow endpoints for receiving, processing and sending emails."""

from fastapi import APIRouter, Depends, HTTPException, Query
from typing import Optional

from app.api.deps import get_email_processor, get_email_service, get_email_storage
from app.core.config import settings
from app.models import (
    ApproveSuggestionRequest,
    AutoReplyConfig,
    EmailListResponse,
    ReceivedEmail,
    SuggestionListResponse
)

router = APIRouter()


@router.get("/emails", response_model=EmailListResponse, tags=["email"])
async def list_emails(
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
    has_suggestion: Optional[bool] = Query(None),
    email_storage=Depends(get_email_storage)
) -> EmailListResponse:
    """List received emails."""
    emails = email_storage.list_emails(
        limit=limit,
        offset=offset,
        has_suggestion=has_suggestion
    )
    total = len(email_storage.list_emails(limit=10000))  # Get total count
    
    return EmailListResponse(emails=emails, total=total)


@router.get("/emails/{email_id}", response_model=ReceivedEmail, tags=["email"])
async def get_email(
    email_id: str,
    email_storage=Depends(get_email_storage)
) -> ReceivedEmail:
    """Get email by ID."""
    email_obj = email_storage.get_email(email_id)
    if not email_obj:
        raise HTTPException(status_code=404, detail="Email não encontrado")
    return email_obj


@router.get("/suggestions", response_model=SuggestionListResponse, tags=["email"])
async def list_suggestions(
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
    status: Optional[str] = Query(None, regex="^(pending|approved|rejected|sent)$"),
    email_storage=Depends(get_email_storage)
) -> SuggestionListResponse:
    """List email suggestions."""
    suggestions = email_storage.list_suggestions(
        limit=limit,
        offset=offset,
        status=status
    )
    total = len(email_storage.list_suggestions(limit=10000))  # Get total count
    
    return SuggestionListResponse(suggestions=suggestions, total=total)


@router.get("/suggestions/{suggestion_id}", tags=["email"])
async def get_suggestion(
    suggestion_id: str,
    email_storage=Depends(get_email_storage)
):
    """Get suggestion by ID."""
    suggestion = email_storage.get_suggestion(suggestion_id)
    if not suggestion:
        raise HTTPException(status_code=404, detail="Sugestão não encontrada")
    
    # Also get the associated email
    email_obj = email_storage.get_email(suggestion.email_id)
    
    return {
        "suggestion": suggestion,
        "email": email_obj
    }


@router.get("/emails/{email_id}/suggestion", tags=["email"])
async def get_suggestion_by_email_id(
    email_id: str,
    email_storage=Depends(get_email_storage)
):
    """Get suggestion by email ID."""
    suggestion = email_storage.get_suggestion_by_email_id(email_id)
    if not suggestion:
        raise HTTPException(status_code=404, detail="Sugestão não encontrada para este email")
    
    return suggestion


@router.post("/suggestions/{suggestion_id}/approve", tags=["email"])
async def approve_suggestion(
    suggestion_id: str,
    request: ApproveSuggestionRequest,
    email_processor=Depends(get_email_processor),
    email_service=Depends(get_email_service)
):
    """Approve a suggestion and optionally send the email."""
    if request.suggestion_id != suggestion_id:
        raise HTTPException(
            status_code=400,
            detail="suggestion_id no path deve corresponder ao suggestion_id no body"
        )
    
    success = email_processor.approve_and_send_suggestion(
        suggestion_id=suggestion_id,
        send_email=request.send_email,
        email_service=email_service
    )
    
    if not success:
        raise HTTPException(
            status_code=400,
            detail="Falha ao aprovar e enviar sugestão"
        )
    
    return {
        "success": True,
        "message": "Sugestão aprovada e email enviado com sucesso" if request.send_email else "Sugestão aprovada com sucesso"
    }


@router.post("/suggestions/{suggestion_id}/reject", tags=["email"])
async def reject_suggestion(
    suggestion_id: str,
    email_processor=Depends(get_email_processor)
):
    """Reject a suggestion."""
    success = email_processor.reject_suggestion(suggestion_id)
    
    if not success:
        raise HTTPException(
            status_code=400,
            detail="Falha ao rejeitar sugestão"
        )
    
    return {
        "success": True,
        "message": "Sugestão rejeitada com sucesso"
    }


@router.post("/emails/check", tags=["email"])
async def check_new_emails(
    limit: int = Query(10, ge=1, le=50),
    email_service=Depends(get_email_service),
    email_processor=Depends(get_email_processor)
):
    """Manually trigger check for new emails."""
    try:
        # Fetch new emails
        emails_data = email_service.fetch_emails(limit=limit, unread_only=True)
        
        processed_count = 0
        for email_data in emails_data:
            try:
                email_processor.process_received_email(email_data)
                processed_count += 1
            except Exception as e:
                # Continue processing other emails even if one fails
                continue
        
        return {
            "success": True,
            "message": f"{processed_count} email(s) processado(s) com sucesso",
            "fetched": len(emails_data),
            "processed": processed_count
        }
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Erro ao verificar novos emails: {str(e)}"
        )


@router.delete("/emails/{email_id}", tags=["email"])
async def delete_email(
    email_id: str,
    email_storage=Depends(get_email_storage)
):
    """Delete a specific email and its associated suggestion."""
    success = email_storage.delete_email(email_id)
    
    if not success:
        raise HTTPException(
            status_code=404,
            detail="Email não encontrado"
        )
    
    return {
        "success": True,
        "message": f"Email {email_id} deletado com sucesso"
    }


@router.delete("/emails", tags=["email"])
async def clear_all_emails(
    email_storage=Depends(get_email_storage)
):
    """Clear all emails and their associated suggestions."""
    try:
        count = email_storage.clear_all_emails()
        return {
            "success": True,
            "message": f"{count} email(s) deletado(s) com sucesso",
            "deleted_count": count
        }
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Erro ao limpar emails: {str(e)}"
        )


@router.get("/auto-reply/config", response_model=AutoReplyConfig, tags=["email"])
async def get_auto_reply_config():
    """Get current auto-reply configuration."""
    return AutoReplyConfig(
        enabled=settings.email_auto_reply_enabled,
        only_productive=settings.email_auto_reply_only_productive,
        min_confidence=settings.email_auto_reply_min_confidence
    )


@router.put("/auto-reply/config", response_model=AutoReplyConfig, tags=["email"])
async def update_auto_reply_config(config: AutoReplyConfig):
    """
    Update auto-reply configuration.
    
    Note: This updates the settings object in memory. For persistent changes,
    update the .env file or environment variables.
    """
    settings.email_auto_reply_enabled = config.enabled
    settings.email_auto_reply_only_productive = config.only_productive
    settings.email_auto_reply_min_confidence = config.min_confidence
    
    return AutoReplyConfig(
        enabled=settings.email_auto_reply_enabled,
        only_productive=settings.email_auto_reply_only_productive,
        min_confidence=settings.email_auto_reply_min_confidence
    )
