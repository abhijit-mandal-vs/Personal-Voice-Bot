"""Pydantic models for API requests and responses."""

from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field


class ChatMessage(BaseModel):
    """A single chat message model."""

    role: str = Field(
        ..., description="The role of the message sender (system, user, assistant)"
    )
    content: str = Field(..., description="The content of the message")


class ChatRequest(BaseModel):
    """Chat request model for text-based interactions."""

    message: str = Field(..., description="The user's message")
    conversation_id: Optional[str] = Field(
        None, description="Optional conversation ID for continuing conversations"
    )


class ChatResponse(BaseModel):
    """Chat response model for text-based interactions."""

    response: str = Field(..., description="The assistant's response")
    conversation_id: str = Field(..., description="Conversation ID for future messages")


class AudioRequest(BaseModel):
    """Request model containing audio data."""

    conversation_id: Optional[str] = Field(
        None, description="Optional conversation ID for continuing conversations"
    )
    # Note: The actual audio data will be sent as form data, not in the JSON payload


class AudioResponse(BaseModel):
    """Response model containing audio data and text."""

    text: str = Field(..., description="The text version of the response")
    conversation_id: str = Field(..., description="Conversation ID for future messages")
    # Note: The actual audio data will be sent in the response body, not in the JSON payload


class ErrorResponse(BaseModel):
    """Error response model."""

    error: str = Field(..., description="Error message")
    details: Optional[Dict[str, Any]] = Field(
        None, description="Additional error details"
    )
