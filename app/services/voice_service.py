"""Service for handling voice processing."""

import asyncio
from typing import Optional, Dict, Any

from app.core.config import settings
from app.core.voice import (
    speech_to_text as stt,
    text_to_speech as tts,
    preprocess_audio,
)


class VoiceService:
    """Service for processing voice data."""

    async def speech_to_text(self, audio_data: bytes) -> str:
        """
        Convert speech to text asynchronously.

        Args:
            audio_data (bytes): Raw audio data

        Returns:
            str: Transcribed text
        """
        # Preprocess the audio
        processed_audio = preprocess_audio(audio_data)

        # Run in a thread pool to avoid blocking
        loop = asyncio.get_event_loop()
        text = await loop.run_in_executor(None, stt, processed_audio)

        return text

    async def text_to_speech(self, text: str) -> bytes:
        """
        Convert text to speech asynchronously.

        Args:
            text (str): Text to convert to speech

        Returns:
            bytes: Audio data
        """
        # Run in a thread pool to avoid blocking
        loop = asyncio.get_event_loop()
        audio_data = await loop.run_in_executor(None, tts, text)

        return audio_data
