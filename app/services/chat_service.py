"""Service for handling ChatGPT interactions."""

import asyncio
import json
from typing import List, Dict, Any, Optional
import openai
from openai import AsyncOpenAI

from app.core.config import settings
from app.core.responses import get_response_context


class ChatService:
    """Service for interacting with ChatGPT."""

    def __init__(self):
        """Initialize the ChatService."""
        # Initialize OpenAI client
        self.client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)

        # Store conversations by ID
        self.conversations: Dict[str, List[Dict[str, str]]] = {}

    async def generate_response(self, user_message: str, conversation_id: str) -> str:
        """
        Generate a response using ChatGPT.

        Args:
            user_message (str): The user's message
            conversation_id (str): The conversation ID

        Returns:
            str: The generated response
        """
        # Initialize conversation if it doesn't exist
        if conversation_id not in self.conversations:
            self.conversations[conversation_id] = []

            # Add system prompt with personal context
            personal_context = get_response_context(user_message)
            self.conversations[conversation_id].append(
                {
                    "role": "system",
                    "content": (
                        f"You are a personal voice assistant that responds as if you were the person "
                        f"being asked about. Use the following context to guide your responses:\n\n"
                        f"{personal_context}\n\n"
                        f"Always respond in first person as if you are the person being asked about. "
                        f"Keep responses concise and conversational, around 2-3 sentences."
                    ),
                }
            )

        # Add the user message to the conversation
        self.conversations[conversation_id].append(
            {"role": "user", "content": user_message}
        )

        try:
            # Generate a response using ChatGPT
            response = await self.client.chat.completions.create(
                model=settings.OPENAI_MODEL,
                messages=self.conversations[conversation_id],
                max_tokens=150,
                temperature=0.7,
            )

            # Extract the response text
            response_text = response.choices[0].message.content.strip()

            # Add the assistant's response to the conversation
            self.conversations[conversation_id].append(
                {"role": "assistant", "content": response_text}
            )

            # Trim conversation history if it gets too long
            if len(self.conversations[conversation_id]) > 10:
                # Keep system message and last 9 messages
                system_message = self.conversations[conversation_id][0]
                self.conversations[conversation_id] = [
                    system_message
                ] + self.conversations[conversation_id][-9:]

            return response_text

        except openai.APIError as e:
            # Handle API errors
            error_message = f"OpenAI API Error: {str(e)}"
            print(error_message)
            return "I'm sorry, I'm having trouble responding right now. Please try again later."

        except Exception as e:
            # Handle other errors
            error_message = f"Error generating response: {str(e)}"
            print(error_message)
            return "I encountered an unexpected error. Please try again."

    def get_conversation_history(self, conversation_id: str) -> List[Dict[str, str]]:
        """
        Get the conversation history.

        Args:
            conversation_id (str): The conversation ID

        Returns:
            List[Dict[str, str]]: The conversation history
        """
        return self.conversations.get(conversation_id, [])
