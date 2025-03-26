"""Tests for the service layer."""

import sys
import os
import pytest
import uuid
import asyncio
from unittest.mock import patch, MagicMock, AsyncMock
import json
import io

# Add the project root directory to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.services.chat_service import ChatService
from app.services.voice_service import VoiceService


# Test ChatService
@pytest.mark.asyncio
@patch("openai.AsyncOpenAI")
async def test_chat_service_generate_response(mock_openai):
    """Test the ChatService.generate_response method."""
    # Mock the OpenAI client
    mock_client = AsyncMock()
    mock_openai.return_value = mock_client

    # Mock the API response
    mock_completion = MagicMock()
    mock_completion.choices = [MagicMock()]
    mock_completion.choices[0].message.content = "This is a test response"

    # Set up the mock to return our mock completion
    mock_client.chat.completions.create = AsyncMock(return_value=mock_completion)

    # Create chat service
    chat_service = ChatService()

    # Generate a test conversation ID
    conversation_id = str(uuid.uuid4())

    # Call the method
    response = await chat_service.generate_response(
        "What's your superpower?", conversation_id
    )

    # Verify response
    assert response == "This is a test response"

    # Verify the conversation was stored
    assert conversation_id in chat_service.conversations
    assert (
        len(chat_service.conversations[conversation_id]) >= 3
    )  # System, user, assistant

    # Verify the API was called with the right parameters
    mock_client.chat.completions.create.assert_called_once()
    call_args = mock_client.chat.completions.create.call_args[1]
    assert call_args["model"] == "gpt-3.5-turbo"
    assert isinstance(call_args["messages"], list)
    assert call_args["max_tokens"] == 150


# Test VoiceService
@pytest.mark.asyncio
@patch("app.core.voice.speech_to_text")
async def test_voice_service_speech_to_text(mock_stt):
    """Test the VoiceService.speech_to_text method."""
    # Mock the speech to text function
    mock_stt.return_value = "This is a test transcription"

    # Create voice service
    voice_service = VoiceService()

    # Call the method
    text = await voice_service.speech_to_text(b"test_audio_data")

    # Verify response
    assert text == "This is a test transcription"

    # Verify the STT function was called
    mock_stt.assert_called_once()


@pytest.mark.asyncio
@patch("app.core.voice.text_to_speech")
async def test_voice_service_text_to_speech(mock_tts):
    """Test the VoiceService.text_to_speech method."""
    # Mock the text to speech function
    mock_tts.return_value = b"test_audio_data"

    # Create voice service
    voice_service = VoiceService()

    # Call the method
    audio = await voice_service.text_to_speech("This is a test message")

    # Verify response
    assert audio == b"test_audio_data"

    # Verify the TTS function was called
    mock_tts.assert_called_once_with("This is a test message")
