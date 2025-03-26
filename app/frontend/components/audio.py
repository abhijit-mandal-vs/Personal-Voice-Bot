"""Audio components for Streamlit frontend."""

import base64
import tempfile
import os
import io
from io import BytesIO
import streamlit as st
import requests
from pydub import AudioSegment
from pydub.playback import play
from streamlit_mic_recorder import mic_recorder
from openai import OpenAI
import dotenv
from app.core.config import settings
from gtts import gTTS


def whisper_stt(
    openai_api_key=None,
    start_prompt="Start recording",
    stop_prompt="Stop recording",
    just_once=False,
    use_container_width=False,
    language=None,
    callback=None,
    args=(),
    kwargs=None,
    key=None,
):
    """
    Record audio and transcribe it using OpenAI's Whisper API.

    Args:
        openai_api_key (str, optional): OpenAI API key
        start_prompt (str): Text for start recording button
        stop_prompt (str): Text for stop recording button
        just_once (bool): Whether to record just once
        use_container_width (bool): Whether to use container width
        language (str, optional): Language code for transcription
        callback (callable, optional): Callback function
        args (tuple): Arguments for callback
        kwargs (dict, optional): Keyword arguments for callback
        key (str, optional): Unique key for the component

    Returns:
        str: Transcribed text
    """
    if not "openai_client" in st.session_state:
        dotenv.load_dotenv()
        st.session_state.openai_client = OpenAI(
            api_key=openai_api_key
            or settings.OPENAI_API_KEY
            or os.getenv("OPENAI_API_KEY")
        )
    if not "_last_speech_to_text_transcript_id" in st.session_state:
        st.session_state._last_speech_to_text_transcript_id = 0
    if not "_last_speech_to_text_transcript" in st.session_state:
        st.session_state._last_speech_to_text_transcript = None
    if key and not key + "_output" in st.session_state:
        st.session_state[key + "_output"] = None

    audio = mic_recorder(
        start_prompt=start_prompt,
        stop_prompt=stop_prompt,
        just_once=just_once,
        use_container_width=use_container_width,
        key=key,
    )

    new_output = False
    if audio is None:
        output = None
    else:
        id = audio["id"]
        new_output = id > st.session_state._last_speech_to_text_transcript_id
        if new_output:
            output = None
            st.session_state._last_speech_to_text_transcript_id = id
            audio_bio = io.BytesIO(audio["bytes"])
            audio_bio.name = "audio.mp3"
            success = False
            err = 0
            while (
                not success and err < 3
            ):  # Retry up to 3 times in case of OpenAI server error.
                try:
                    transcript = (
                        st.session_state.openai_client.audio.transcriptions.create(
                            model="whisper-1", file=audio_bio, language=language
                        )
                    )
                except Exception as e:
                    print(str(e))  # log the exception in the terminal
                    err += 1
                else:
                    success = True
                    output = transcript.text
                    st.session_state._last_speech_to_text_transcript = output
        elif not just_once:
            output = st.session_state._last_speech_to_text_transcript
        else:
            output = None

    if key:
        st.session_state[key + "_output"] = output
    if new_output and callback:
        callback(*args, **(kwargs or {}))
    return output


def audio_recorder():
    """
    Record audio from the user's microphone.

    Returns:
        tuple: (audio_bytes, transcript) - The recorded audio data and transcribed text
    """
    # Use the whisper_stt function to record and transcribe audio
    text = whisper_stt(
        start_prompt="Click to record your question 🎤",
        stop_prompt="Stop recording 🔴",
        just_once=True,
        language="en",
        key="recorder",
    )

    # If text is available, we captured audio
    if text and "recorder" in st.session_state:
        # The audio data is directly in the recorder object, not in a 'bytes' key
        return st.session_state.recorder, text

    return None, None


def play_audio(audio_bytes):
    """
    Play audio in the Streamlit app.

    Args:
        audio_bytes (bytes): The audio data to play
    """
    if audio_bytes:
        # Create a base64 encoded string of the audio data
        b64 = base64.b64encode(audio_bytes).decode()

        # Use HTML audio component
        audio_html = f"""
        <audio autoplay>
            <source src="data:audio/wav;base64,{b64}" type="audio/wav">
            Your browser does not support the audio element.
        </audio>
        """

        # Display audio player
        st.markdown(audio_html, unsafe_allow_html=True)

        # Also provide a download button
        st.download_button(
            label="Download Audio",
            data=audio_bytes,
            file_name="response.wav",
            mime="audio/wav",
        )


def audio_to_file(audio_bytes):
    """
    Save audio bytes to a temporary file.

    Args:
        audio_bytes (bytes): The audio data

    Returns:
        str: Path to the temporary file
    """
    with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as f:
        f.write(audio_bytes)
        return f.name


def send_audio_to_api(
    audio_bytes, conversation_id=None, api_url="http://localhost:8000/api/voice"
):
    """
    Send audio to the backend API.

    Args:
        audio_bytes (bytes): The audio data
        conversation_id (str, optional): Conversation ID for continuing conversations
        api_url (str): The API URL

    Returns:
        tuple: Response text and audio bytes
    """
    try:
        # Create form data with the audio file
        files = {"audio": ("audio.wav", audio_bytes, "audio/wav")}

        # Add conversation ID if provided
        data = {}
        if conversation_id:
            data["conversation_id"] = conversation_id

        # Send the request
        response = requests.post(api_url, files=files, data=data)

        # Check for errors
        response.raise_for_status()

        # Extract conversation ID and response text from headers
        conversation_id = response.headers.get("X-Conversation-ID")
        response_text = response.headers.get("X-Response-Text")

        # Return the response text and audio
        return response_text, response.content, conversation_id

    except requests.RequestException as e:
        st.error(f"Error communicating with the API: {str(e)}")
        return None, None, None


def text_to_speech_button(text, key=None):
    """
    Display a speaker button that converts text to speech when clicked.
    Using OpenAI's TTS API with a male voice.

    Args:
        text (str): The text to convert to speech
        key (str, optional): Unique key for the button
    """
    # Create a unique key if not provided
    button_key = key or f"tts_button_{hash(text)}"

    # Check if we already converted this text to audio
    if button_key not in st.session_state:
        st.session_state[button_key] = None

    # Display a speaker button with emoji - no columns to prevent vertical layout issues
    if st.button("🔊", key=button_key + "_btn"):
        try:
            # Initialize OpenAI client if not already done
            if "openai_client" not in st.session_state:
                dotenv.load_dotenv()
                st.session_state.openai_client = OpenAI(
                    api_key=settings.OPENAI_API_KEY or os.getenv("OPENAI_API_KEY")
                )

            # Convert text to speech using OpenAI's TTS with a male voice
            response = st.session_state.openai_client.audio.speech.create(
                model="tts-1",
                voice="onyx",  # Using onyx which is a deep male voice
                input=text,
            )

            # Get the audio data
            audio_data = response.content
            st.session_state[button_key] = audio_data

            # No success message to keep the UI clean

        except Exception as e:
            # Only show error if something goes wrong
            st.error(f"Error generating speech: {e}")

    # If we have audio data, display it
    if st.session_state[button_key] is not None:
        st.audio(st.session_state[button_key], format="audio/mp3")
