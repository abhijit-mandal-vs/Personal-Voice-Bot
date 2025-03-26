"""Chat interface components for Streamlit frontend."""

import streamlit as st
import requests
import json
from app.frontend.components.audio import text_to_speech_button
from gtts import gTTS
import io
from app.core.config import settings


def initialize_chat():
    """
    Initialize the chat session state.
    """
    # Initialize session state for chat
    if "messages" not in st.session_state:
        st.session_state.messages = []

    if "conversation_id" not in st.session_state:
        st.session_state.conversation_id = None


def display_chat():
    """
    Display the chat interface with message history.
    """
    # Title
    st.title("🤖 Personal Voice Bot")

    # Displaying chat messages
    for i, message in enumerate(st.session_state.messages):
        with st.chat_message(message["role"]):
            st.write(message["content"])

            # Add a speaker button for assistant messages
            if message["role"] == "assistant":
                text_to_speech_button(message["content"], key=f"tts_{i}")


def add_message(role, content):
    """
    Add a message to the chat history.

    Args:
        role (str): The role of the message sender (user or assistant)
        content (str): The content of the message
    """
    # Adding message to session state
    st.session_state.messages.append({"role": role, "content": content})


def send_text_to_api(
    text, conversation_id=None, api_url="http://localhost:8000/api/chat"
):
    """
    Send text to the backend API, using the appropriate endpoint based on current model.

    Args:
        text (str): The text to send
        conversation_id (str, optional): Conversation ID for continuing conversations
        api_url (str): The API URL

    Returns:
        tuple: Response text and conversation ID
    """
    try:
        # Determining which endpoint to use based on current model
        if (
            "llama" in settings.CURRENT_MODEL
            or "groq" in settings.CURRENT_MODEL.lower()
        ):
            # Override with Groq endpoint
            if api_url.endswith("/chat"):
                api_url = api_url.replace("/chat", "/chat-groq")

        # Creating the request payload
        payload = {"message": text}

        if conversation_id:
            payload["conversation_id"] = conversation_id

        # Sending the request
        response = requests.post(
            api_url, json=payload, headers={"Content-Type": "application/json"}
        )

        # Checking for errors
        response.raise_for_status()

        # Parsing the response
        result = response.json()

        # Return the response text and conversation ID
        return result["response"], result["conversation_id"]

    except requests.RequestException as e:
        st.error(f"Error communicating with the API: {str(e)}")
        return None, None


def text_input_area():
    """
    Display a text input area for the user to type a message.

    Returns:
        str: The user's message or None if no message was entered
    """
    # Get user input
    user_input = st.chat_input("Type your question here...")
    return user_input


def example_questions():
    """
    Display a list of example questions the user can click on.

    Returns:
        str: The selected question or None if no question was selected
    """
    # Creating columns for better layout
    col1, col2 = st.columns(2)
    col3 = st.container()

    with col1:
        if st.button("What should we know about your life story? ☺️"):
            return "What should we know about your life story in a few sentences?"

        if st.button("Top 3 areas you'd like to grow in? 🌱"):
            return "What are the Top 3 areas you'd like to grow in?"

    with col2:
        if st.button("What's your #1 superpower? 💪"):
            return "What's your #1 superpower?"

        if st.button("How do you push your boundaries & limits? ⚡️"):
            return "How do you push your boundaries and limits?"

    with col3:
        if st.button("What misconception do coworkers have about you? 🤔"):
            return "What misconception do coworkers have about you?"

    return None
