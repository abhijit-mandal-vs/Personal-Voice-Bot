"""Voice processing utilities for the voice bot."""

import io
import os
import tempfile
import numpy as np
from pydub import AudioSegment
import speech_recognition as sr
from gtts import gTTS

from app.core.config import settings


def speech_to_text(audio_data):
    """
    Convert speech to text using speech recognition.

    Args:
        audio_data (bytes): Raw audio data

    Returns:
        str: Transcribed text
    """
    recognizer = sr.Recognizer()

    # Creating a temporary file to store the audio
    with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as temp_audio:
        temp_audio.write(audio_data)
        temp_audio_path = temp_audio.name

    try:
        # Converting the audio to AudioData for the recognizer
        with sr.AudioFile(temp_audio_path) as source:
            audio = recognizer.record(source)

        # Using Google's speech recognition API
        text = recognizer.recognize_google(audio, language=settings.STT_LANGUAGE)
        return text
    except sr.UnknownValueError:
        return "Sorry, I could not understand the audio."
    except sr.RequestError as e:
        return f"Speech recognition service error: {e}"
    finally:
        # Clean up the temporary file
        if os.path.exists(temp_audio_path):
            os.remove(temp_audio_path)


def text_to_speech(text):
    """
    Convert text to speech using gTTS.

    Args:
        text (str): Text to convert to speech

    Returns:
        bytes: Audio data as bytes
    """
    # Creating a gTTS object with the text and desired language
    tts = gTTS(text=text, lang=settings.TTS_LANGUAGE, slow=False)

    # Save to a BytesIO object
    mp3_fp = io.BytesIO()
    tts.write_to_fp(mp3_fp)
    mp3_fp.seek(0)

    # Converting to WAV format for better compatibility
    audio = AudioSegment.from_mp3(mp3_fp)

    # Adjusting the speed if needed
    if settings.TTS_SPEED != 1.0:
        audio = audio._spawn(
            audio.raw_data,
            overrides={"frame_rate": int(audio.frame_rate * settings.TTS_SPEED)},
        )

    # Export to bytes
    buffer = io.BytesIO()
    audio.export(buffer, format="wav")

    return buffer.getvalue()


def preprocess_audio(audio_data):
    """
    Preprocess audio data for better recognition.

    Args:
        audio_data (bytes): Raw audio data

    Returns:
        bytes: Processed audio data
    """
    # Converting bytes to audio segment
    with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as temp_file:
        temp_file.write(audio_data)
        temp_path = temp_file.name

    try:
        audio = AudioSegment.from_file(temp_path, format="wav")

        # Normalizing the volume
        audio = audio.normalize()

        # Removing the silence
        audio = detect_leading_silence(audio)

        # Export to bytes
        buffer = io.BytesIO()
        audio.export(buffer, format="wav")
        return buffer.getvalue()
    finally:
        if os.path.exists(temp_path):
            os.remove(temp_path)


def detect_leading_silence(audio, silence_threshold=-50.0, chunk_size=10):
    """
    Detect and remove leading and trailing silence from audio.

    Args:
        audio (AudioSegment): Audio to process
        silence_threshold (float): Silence threshold in dB
        chunk_size (int): Chunk size in milliseconds

    Returns:
        AudioSegment: Audio without silence
    """
    trim_ms = 0

    # Detecting leading silence
    while (
        trim_ms < len(audio)
        and audio[trim_ms : trim_ms + chunk_size].dBFS < silence_threshold
    ):
        trim_ms += chunk_size

    # Detect trailing silence
    end_trim_ms = len(audio)
    while (
        end_trim_ms > 0
        and audio[end_trim_ms - chunk_size : end_trim_ms].dBFS < silence_threshold
    ):
        end_trim_ms -= chunk_size

    # Returning the trimmed audio
    return audio[trim_ms:end_trim_ms]
