"""Pydantic models for email classification API."""

from enum import Enum
from typing import Optional

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

