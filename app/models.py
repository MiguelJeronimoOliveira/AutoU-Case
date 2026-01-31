"""Pydantic models for email classification API."""

from datetime import datetime
from enum import Enum
from typing import List, Optional

from pydantic import BaseModel, Field, field_validator


class EmailCategory(str, Enum):
    
    PRODUCTIVE = "productive"
    UNPRODUCTIVE = "unproductive"


class EmailAnalysis(BaseModel):
    
    content: str = Field(..., description="Email content preview")
    full_content: Optional[str] = Field(None, description="Full email content")
    category: EmailCategory = Field(..., description="Classification category")
    confidence: float = Field(
        ...,
        ge=0.0,
        le=1.0,
        description="Confidence score between 0.0 and 1.0"
    )
    suggested_response: Optional[str] = Field(
        None,
        description="Generated response suggestion"
    )
    reasoning: Optional[str] = Field(
        None,
        description="Explanation of the classification"
    )
    
    @field_validator("confidence")
    @classmethod
    def validate_confidence(cls, v: float) -> float:
        if not 0.0 <= v <= 1.0:
            raise ValueError("Confidence must be between 0.0 and 1.0")
        return v


class EmailRequest(BaseModel):
    
    file_path: Optional[str] = Field(
        None,
        description="Path to .txt or .pdf file containing the email"
    )
    email_content: Optional[str] = Field(
        None,
        description="Direct email content as text"
    )
    


class EmailResponse(BaseModel):
    
    success: bool = Field(..., description="Whether the analysis was successful")
    analysis: Optional[EmailAnalysis] = Field(
        None,
        description="Analysis results"
    )
    error: Optional[str] = Field(
        None,
        description="Error message if analysis failed"
    )


class ReceivedEmail(BaseModel):
    """Model for received email."""
    
    id: str = Field(..., description="Unique email ID")
    message_id: Optional[str] = Field(None, description="Email Message-ID header")
    subject: str = Field(..., description="Email subject")
    sender: str = Field(..., description="Email sender address")
    recipient: str = Field(..., description="Email recipient address")
    content: str = Field(..., description="Email body content")
    received_at: datetime = Field(..., description="When email was received")
    category: Optional[EmailCategory] = Field(None, description="Email category")
    confidence: Optional[float] = Field(None, description="Classification confidence")
    has_suggestion: bool = Field(False, description="Whether suggestion was generated")
    suggestion_id: Optional[str] = Field(None, description="ID of generated suggestion")


class EmailSuggestion(BaseModel):
    """Model for email response suggestion."""
    
    id: str = Field(..., description="Unique suggestion ID")
    email_id: str = Field(..., description="ID of the received email")
    suggested_response: str = Field(..., description="Generated response text")
    status: str = Field(default="pending", description="Status: pending, approved, rejected, sent")
    created_at: datetime = Field(..., description="When suggestion was created")
    approved_at: Optional[datetime] = Field(None, description="When suggestion was approved")
    sent_at: Optional[datetime] = Field(None, description="When email was sent")


class EmailListResponse(BaseModel):
    """Response model for listing emails."""
    
    emails: List[ReceivedEmail] = Field(..., description="List of received emails")
    total: int = Field(..., description="Total number of emails")


class SuggestionListResponse(BaseModel):
    """Response model for listing suggestions."""
    
    suggestions: List[EmailSuggestion] = Field(..., description="List of suggestions")
    total: int = Field(..., description="Total number of suggestions")


class ApproveSuggestionRequest(BaseModel):
    """Request model for approving a suggestion."""
    
    suggestion_id: str = Field(..., description="ID of suggestion to approve")
    send_email: bool = Field(default=True, description="Whether to send email immediately after approval")


class AutoReplyConfig(BaseModel):
    """Model for auto-reply configuration."""
    
    enabled: bool = Field(..., description="Whether auto-reply is enabled")
    only_productive: bool = Field(default=True, description="Only auto-reply to productive emails")
    min_confidence: float = Field(
        default=0.7,
        ge=0.0,
        le=1.0,
        description="Minimum confidence score required for auto-reply"
    )
