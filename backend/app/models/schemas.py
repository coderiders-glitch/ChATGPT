"""
Pydantic models for request/response validation and serialization.
"""
from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, Field, field_validator


class ChatRequest(BaseModel):
    """Request model for chat endpoint."""
    query: str = Field(..., min_length=1, max_length=4000, description="User's natural language query")
    conversation_id: Optional[str] = Field(None, description="Optional conversation ID for context")

    @field_validator("query")
    @classmethod
    def validate_query(cls, v: str) -> str:
        """Ensure query is not empty after stripping whitespace."""
        if not v or not v.strip():
            raise ValueError("Query cannot be empty or whitespace only")
        return v.strip()


class ChatResponse(BaseModel):
    """Response model for chat endpoint."""
    response: str = Field(..., description="AI-generated response text")
    confidence: float = Field(..., ge=0.0, le=1.0, description="Confidence score between 0 and 1")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="Response timestamp")
    conversation_id: Optional[str] = Field(None, description="Conversation ID for future context")


class HealthResponse(BaseModel):
    """Response model for health check endpoint."""
    status: str = Field(..., description="Service health status")
    service: str = Field(..., description="Service name")
    version: str = Field(default="1.0.0", description="API version")


class ErrorResponse(BaseModel):
    """Standard error response model."""
    detail: str = Field(..., description="Error message")
    error_code: Optional[str] = Field(None, description="Specific error code")
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class InteractionLog(BaseModel):
    """Model for interaction logging."""
    log_id: Optional[int] = Field(None, description="Unique log identifier")
    user_id: str = Field(..., description="Authenticated user ID")
    query_text: str = Field(..., description="Original user query")
    response_text: str = Field(..., description="AI response")
    confidence_score: float = Field(..., description="Response confidence")
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class TokenPayload(BaseModel):
    """Model for JWT token payload."""
    sub: str = Field(..., description="Subject (user ID)")
    exp: datetime = Field(..., description="Expiration timestamp")
    iat: datetime = Field(default_factory=datetime.utcnow, description="Issued at timestamp")