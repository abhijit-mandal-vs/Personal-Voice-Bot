"""Main entry point for the Streamlit frontend application."""

import os
import sys
import streamlit as st
from dotenv import load_dotenv

# Add the project root directory to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

# Now you can import from app
from app.core.config import settings

# Load environment variables
load_dotenv()

# Import components
from app.frontend.components.audio import audio_recorder, play_audio, send_audio_to_api
from app.frontend.components.chat import (
    initialize_chat,
    display_chat,
    add_message,
    send_text_to_api,
    text_input_area,
    example_questions,
)

# Page config
st.set_page_config(
    page_title="Personal Voice Bot",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="auto",
)

# CSS for styling
st.markdown(
    """
<style>
    .stButton>button {
        width: 100%;
    }
    .stAudio {
        margin-top: 1rem;
        margin-bottom: 1rem;
    }
    div[data-testid="stExpander"] div[role="button"] p {
        font-size: 1.2rem;
    }
</style>
""",
    unsafe_allow_html=True,
)


def main():
    """Main function to run the Streamlit app."""
    # Initialize chat
    initialize_chat()

    # Display chat interface
    display_chat()

    # Sidebar with instructions
    with st.sidebar:
        st.title("How to Use 🧑🏻‍💻")
        st.write(
            """
        1. Type a question or click one of the example questions below 💬
        2. OR click the microphone to ask a question with your voice 🎤
        3. The bot will respond as if it were you 🤖
        """
        )

        # API settings
        st.header("API Settings 🔧")
        api_host = st.text_input("API Host 🌐", value="localhost")
        api_port = st.number_input(
            "API Port 🔢", value=8000, min_value=1, max_value=65535
        )

        # Set API URL
        api_url = f"http://{api_host}:{api_port}/api"

        # Add a way to clear conversation
        if st.button("Clear Conversation 🧹"):
            st.session_state.messages = []
            st.session_state.conversation_id = None
            st.rerun()

    # Example questions
    st.subheader("Example Questions")
    question = example_questions()

    if question:
        # Add user message to chat
        add_message("user", question)

        # Send question to API
        if (
            "llama" in settings.CURRENT_MODEL
            or "groq" in settings.CURRENT_MODEL.lower()
        ):
            print("Using Groq endpoint")
            # Use Groq endpoint
            response, conversation_id = send_text_to_api(
                question, st.session_state.conversation_id, f"{api_url}/chat-groq"
            )
        else:
            print("Using OpenAI endpoint")
            # Use default OpenAI endpoint
            response, conversation_id = send_text_to_api(
                question, st.session_state.conversation_id, f"{api_url}/chat"
            )

        if response and conversation_id:
            # Update conversation ID
            st.session_state.conversation_id = conversation_id

            # Add assistant response to chat
            add_message("assistant", response)

            # Rerun to update UI
            st.rerun()

    # Text input
    user_input = text_input_area()

    if user_input:
        # Add user message to chat
        add_message("user", user_input)

        # Send message to API
        if (
            "llama" in settings.CURRENT_MODEL
            or "groq" in settings.CURRENT_MODEL.lower()
        ):
            # Use Groq endpoint
            response, conversation_id = send_text_to_api(
                user_input, st.session_state.conversation_id, f"{api_url}/chat-groq"
            )
        else:
            # Use default OpenAI endpoint
            response, conversation_id = send_text_to_api(
                user_input, st.session_state.conversation_id, f"{api_url}/chat"
            )

        if response and conversation_id:
            # Update conversation ID
            st.session_state.conversation_id = conversation_id

            # Add assistant response to chat
            add_message("assistant", response)

            # Rerun to update UI
            st.rerun()

    # Voice input
    st.subheader("Or ask with your voice")

    # Record audio
    audio_data, transcript = audio_recorder()

    if audio_data:
        # Add a loading message
        with st.spinner("Processing voice input..."):
            # Add user message to chat with the transcript
            if transcript:
                add_message("user", transcript)

                # You can either use the transcript directly or send the audio to your API
                # Option 1: Use transcript directly
                if (
                    "llama" in settings.CURRENT_MODEL
                    or "groq" in settings.CURRENT_MODEL.lower()
                ):
                    # Use Groq endpoint
                    response, conversation_id = send_text_to_api(
                        transcript,
                        st.session_state.conversation_id,
                        f"{api_url}/chat-groq",
                    )
                else:
                    # Use default OpenAI endpoint
                    response, conversation_id = send_text_to_api(
                        transcript, st.session_state.conversation_id, f"{api_url}/chat"
                    )

                # Option 2: Process the audio (comment out Option 1 if using this)
                # Process the audio
                # transcript, audio_response, conversation_id = send_audio_to_api(
                #    audio_data,
                #    st.session_state.conversation_id,
                #    f"{api_url}/voice"
                # )

                if response and conversation_id:
                    # Update conversation ID
                    st.session_state.conversation_id = conversation_id

                    # Add assistant response to chat
                    add_message("assistant", response)

                    # Play the audio response if available
                    # if audio_response:
                    #    play_audio(audio_response)

                    # Rerun to update UI
                    st.rerun()


if __name__ == "__main__":
    main()
