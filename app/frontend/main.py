"""Main entry point for the Streamlit frontend application."""

import os
import sys
import streamlit as st
from dotenv import load_dotenv

# Adding the project root directory to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

# Now you can import from app
from app.core.config import settings

# Loading environment variables
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
    # Initializing chat
    initialize_chat()

    # Displaying chat interface
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

        # Add deployment mode selection
        deployment_mode = st.radio(
            "Deployment Mode",
            options=["Local", "Cloud"],
            index=0,  # Default to Local
            help="Select 'Cloud' to use the deployed API on Render, or 'Local' for development",
        )

        if deployment_mode == "Cloud":
            # Cloud mode - use the Render deployed API
            st.success("Using cloud API endpoint on Render")
            api_url = "https://personal-voice-bot.onrender.com/api"
            st.write(f"API URL: {api_url}")
        else:
            # Local mode - allow custom configuration
            api_host = st.text_input("API Host 🌐", value="localhost")
            api_port = st.number_input(
                "API Port 🔢", value=8000, min_value=1, max_value=65535
            )
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
        # Adding user message to chat
        add_message("user", question)

        # Sending question to API
        if (
            "llama" in settings.CURRENT_MODEL
            or "groq" in settings.CURRENT_MODEL.lower()
        ):
            print("Using Groq endpoint")
            # Using Groq endpoint
            response, conversation_id = send_text_to_api(
                question, st.session_state.conversation_id, f"{api_url}/chat-groq"
            )
        else:
            print("Using OpenAI endpoint")
            # Using default OpenAI endpoint
            response, conversation_id = send_text_to_api(
                question, st.session_state.conversation_id, f"{api_url}/chat"
            )

        if response and conversation_id:
            # Updating conversation ID
            st.session_state.conversation_id = conversation_id

            # Add assistant response to chat
            add_message("assistant", response)

            # Rerun to update UI
            st.rerun()

    # Text input
    user_input = text_input_area()

    if user_input:
        # Adding user message to chat
        add_message("user", user_input)

        # Send message to API
        if (
            "llama" in settings.CURRENT_MODEL
            or "groq" in settings.CURRENT_MODEL.lower()
        ):
            # Using Groq endpoint
            response, conversation_id = send_text_to_api(
                user_input, st.session_state.conversation_id, f"{api_url}/chat-groq"
            )
        else:
            # Using default OpenAI endpoint
            response, conversation_id = send_text_to_api(
                user_input, st.session_state.conversation_id, f"{api_url}/chat"
            )

        if response and conversation_id:
            # Updating conversation ID
            st.session_state.conversation_id = conversation_id

            # Add assistant response to chat
            add_message("assistant", response)

            # Rerunning to update UI
            st.rerun()

    # Voice input
    st.subheader("Or ask with your voice")

    # Record audio
    audio_data, transcript = audio_recorder()

    if audio_data:
        # Adding a loading message
        with st.spinner("Processing voice input..."):
            # Adding user message to chat with the transcript
            if transcript:
                add_message("user", transcript)

                if (
                    "llama" in settings.CURRENT_MODEL
                    or "groq" in settings.CURRENT_MODEL.lower()
                ):
                    # Using Groq endpoint
                    response, conversation_id = send_text_to_api(
                        transcript,
                        st.session_state.conversation_id,
                        f"{api_url}/chat-groq",
                    )
                else:
                    # Using default OpenAI endpoint
                    response, conversation_id = send_text_to_api(
                        transcript, st.session_state.conversation_id, f"{api_url}/chat"
                    )

                # Process the audio
                # transcript, audio_response, conversation_id = send_audio_to_api(
                #    audio_data,
                #    st.session_state.conversation_id,
                #    f"{api_url}/voice"
                # )

                if response and conversation_id:
                    # Updating conversation ID
                    st.session_state.conversation_id = conversation_id

                    # Adding assistant response to chat
                    add_message("assistant", response)

                    # Playing the audio response if available
                    # if audio_response:
                    #    play_audio(audio_response)

                    # Rerunning to update UI
                    st.rerun()


if __name__ == "__main__":
    main()
