"""API endpoints for the voice bot."""

import uuid
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form, Response
from fastapi.responses import StreamingResponse
import io

from app.api.schemas import ChatRequest, ChatResponse, AudioResponse, ErrorResponse
from app.services.chat_service import ChatService
from app.services.voice_service import VoiceService
from app.core.config import settings

# Creating the API router
router = APIRouter()

# Creating service instances
chat_service = ChatService()
voice_service = VoiceService()


@router.post(
    "/chat", response_model=ChatResponse, responses={400: {"model": ErrorResponse}}
)
async def chat(request: ChatRequest):
    """
    Process a text chat request and return a text response.

    Args:
        request (ChatRequest): The chat request containing the user's message

    Returns:
        ChatResponse: The assistant's response
    """
    try:
        # Generating conversation ID if not provided
        conversation_id = request.conversation_id or str(uuid.uuid4())

        # Processing the request
        response_text = await chat_service.generate_response(
            request.message, conversation_id
        )

        # Returning the response
        return ChatResponse(response=response_text, conversation_id=conversation_id)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post(
    "/voice", response_model=AudioResponse, responses={400: {"model": ErrorResponse}}
)
async def voice(
    audio: UploadFile = File(...), conversation_id: Optional[str] = Form(None)
):
    """
    Process a voice request and return a voice response.

    Args:
        audio (UploadFile): The audio file containing the user's speech
        conversation_id (str, optional): The conversation ID for continuing conversations

    Returns:
        StreamingResponse: The audio response as a streaming response
    """
    try:
        # Reading the audio file
        audio_content = await audio.read()

        # Generating conversation ID if not provided
        conversation_id = conversation_id or str(uuid.uuid4())

        # Processing the audio to text
        text = await voice_service.speech_to_text(audio_content)

        # Generating a response
        response_text = await chat_service.generate_response(text, conversation_id)

        # Converting the response to speech
        audio_response = await voice_service.text_to_speech(response_text)

        # Returning the response
        return StreamingResponse(
            io.BytesIO(audio_response),
            media_type="audio/wav",
            headers={
                "X-Conversation-ID": conversation_id,
                "X-Response-Text": response_text,
            },
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post(
    "/chat-groq", response_model=ChatResponse, responses={400: {"model": ErrorResponse}}
)
async def chat_groq(request: ChatRequest):
    """
    Process a text chat request and return a text response using Groq model.

    Args:
        request (ChatRequest): The chat request containing the user's message

    Returns:
        ChatResponse: The assistant's response
    """
    try:
        # Generating conversation ID if not provided
        conversation_id = request.conversation_id or str(uuid.uuid4())

        # Processing the request with Groq
        response_text = await chat_service.generate_response_groq(
            request.message, conversation_id
        )

        # Returning the response
        return ChatResponse(response=response_text, conversation_id=conversation_id)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/health")
async def health_check():
    """
    Health check endpoint.

    Returns:
        dict: Health status
    """
    return {"status": "healthy", "version": "1.0.0"}
