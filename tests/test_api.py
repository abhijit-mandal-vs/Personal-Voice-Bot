"""Tests for the API endpoints."""

import sys
import os
from fastapi.testclient import TestClient
from unittest.mock import patch
import json
import io
import uuid

# Add the project root directory to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

# Now import from app
from app.main import app

# Create test client
client = TestClient(app)


def test_health_check():
    """Test the health check endpoint."""
    response = client.get("/api/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"


@patch("app.services.chat_service.ChatService.generate_response")
def test_chat_endpoint(mock_generate_response):
    """Test the chat endpoint."""
    # Mock the response
    mock_generate_response.return_value = "This is a test response"

    # Test payload
    test_payload = {
        "message": "What's your superpower?",
        "conversation_id": str(uuid.uuid4()),
    }

    # Send request
    response = client.post("/api/chat", json=test_payload)

    # Check response
    assert response.status_code == 200
    assert "response" in response.json()
    assert "conversation_id" in response.json()
    assert response.json()["response"] == "This is a test response"
    assert response.json()["conversation_id"] == test_payload["conversation_id"]

    # Verify the mock was called with the correct arguments
    mock_generate_response.assert_called_once_with(
        test_payload["message"], test_payload["conversation_id"]
    )


@patch("app.services.voice_service.VoiceService.speech_to_text")
@patch("app.services.chat_service.ChatService.generate_response")
@patch("app.services.voice_service.VoiceService.text_to_speech")
def test_voice_endpoint(
    mock_text_to_speech, mock_generate_response, mock_speech_to_text
):
    """Test the voice endpoint."""
    # Mock the responses
    mock_speech_to_text.return_value = "What's your superpower?"
    mock_generate_response.return_value = "Pattern recognition is my superpower."
    mock_text_to_speech.return_value = b"audio_data"

    # Create test audio file
    test_audio = io.BytesIO(b"test_audio_data")
    test_audio.name = "test.wav"

    # Test conversation ID
    test_conversation_id = str(uuid.uuid4())

    # Send request
    response = client.post(
        "/api/voice",
        files={"audio": ("test.wav", test_audio, "audio/wav")},
        data={"conversation_id": test_conversation_id},
    )

    # Check response
    assert response.status_code == 200
    assert response.headers["X-Conversation-ID"] == test_conversation_id
    assert (
        response.headers["X-Response-Text"] == "Pattern recognition is my superpower."
    )
    assert response.content == b"audio_data"

    # Verify the mocks were called with the correct arguments
    mock_speech_to_text.assert_called_once()
    mock_generate_response.assert_called_once_with(
        "What's your superpower?", test_conversation_id
    )
    mock_text_to_speech.assert_called_once_with("Pattern recognition is my superpower.")
