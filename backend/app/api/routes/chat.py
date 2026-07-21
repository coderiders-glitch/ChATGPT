"""
Chat API routes for handling user queries and LLM integration.
"""
import logging
from datetime import datetime
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from app.models.schemas import ChatRequest, ChatResponse, HealthResponse
from app.services.auth import verify_token
from app.services.llm_client import LLMClient, get_llm_client

logger = logging.getLogger(__name__)
router = APIRouter()
security = HTTPBearer()


@router.post("/chat", response_model=ChatResponse)
async def process_chat(
    request: ChatRequest,
    credentials: HTTPAuthorizationCredentials = Depends(security),
    llm_client: LLMClient = Depends(get_llm_client),
):
    """
    Process a user query and return an AI-generated response.
    
    - Validates user authentication via JWT
    - Sends query to LLM service
    - Logs interaction to database
    - Returns response with confidence score
    """
    try:
        # Verify user token
        user_id = verify_token(credentials.credentials)
        logger.info(f"Processing chat request for user: {user_id}")

        # Validate query input
        if not request.query or len(request.query.strip()) == 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Query cannot be empty"
            )

        # Send query to LLM
        response_text, confidence = await llm_client.generate_response(
            query=request.query,
            user_id=user_id,
            conversation_id=request.conversation_id
        )

        # Log the interaction
        await llm_client.log_interaction(
            user_id=user_id,
            query=request.query,
            response=response_text,
            confidence=confidence
        )

        return ChatResponse(
            response=response_text,
            confidence=confidence,
            timestamp=datetime.utcnow(),
            conversation_id=request.conversation_id
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error processing chat: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Service temporarily unavailable. Please try again."
        )


@router.get("/history/{conversation_id}", response_model=list)
async def get_conversation_history(
    conversation_id: str,
    credentials: HTTPAuthorizationCredentials = Depends(security),
):
    """Retrieve conversation history for a specific conversation."""
    user_id = verify_token(credentials.credentials)
    logger.info(f"Fetching history for conversation: {conversation_id}")
    # Placeholder for conversation history retrieval
    return []