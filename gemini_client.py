"""
Gemini Client for Exam Explainer Bot
Handles communication with Google AI Studio API using Gemini Flash models
"""

import os
from typing import Generator, Optional
import google.generativeai as genai
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class GeminiClient:
    """
    Client for interacting with Google Gemini Flash API
    Provides streaming and non-streaming response generation
    """
    
    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize the Gemini client
        
        Args:
            api_key: Google AI Studio API key. If not provided, reads from GOOGLE_API_KEY env var
        """
        self.api_key = api_key or os.getenv("GOOGLE_API_KEY")
        
        if not self.api_key:
            raise ValueError(
                "Google API key not found. Please set GOOGLE_API_KEY environment variable "
                "or pass api_key parameter."
            )
        
        # Configure the API
        genai.configure(api_key=self.api_key)
        
        # Use Gemini 2.5 Flash-Lite - may have separate quota
        self.model = genai.GenerativeModel(
            model_name="models/gemini-2.5-flash-lite",
            generation_config={
                "temperature": 0.7,
                "top_p": 0.95,
                "top_k": 40,
                "max_output_tokens": 2048,
            },
            safety_settings=[
                {"category": "HARM_CATEGORY_HARASSMENT", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
                {"category": "HARM_CATEGORY_HATE_SPEECH", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
                {"category": "HARM_CATEGORY_SEXUALLY_EXPLICIT", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
                {"category": "HARM_CATEGORY_DANGEROUS_CONTENT", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
            ]
        )
        
        self.chat_session = None
    
    def start_chat(self, system_prompt: str, history: list = None) -> None:
        """
        Start a new chat session with system prompt
        
        Args:
            system_prompt: The system instruction for the bot
            history: Optional chat history to continue from
        """
        self.chat_session = self.model.start_chat(
            history=history or []
        )
        # Prime the model with system prompt
        self._system_prompt = system_prompt
    
    def generate_response(self, user_message: str) -> str:
        """
        Generate a response to user message (non-streaming)
        
        Args:
            user_message: The user's question or message
            
        Returns:
            The model's response text
        """
        if not self.chat_session:
            raise ValueError("Chat session not started. Call start_chat() first.")
        
        # Combine system prompt with user message for context
        full_message = f"{self._system_prompt}\n\nUser: {user_message}"
        
        try:
            response = self.chat_session.send_message(full_message)
            return response.text
        except Exception as e:
            return f"I apologize, but I encountered an error: {str(e)}. Please try again."
    
    def generate_response_stream(self, user_message: str) -> Generator[str, None, None]:
        """
        Generate a streaming response to user message
        
        Args:
            user_message: The user's question or message
            
        Yields:
            Response text chunks as they are generated
        """
        if not self.chat_session:
            raise ValueError("Chat session not started. Call start_chat() first.")
        
        # Combine system prompt with user message for context
        full_message = f"{self._system_prompt}\n\nUser: {user_message}"
        
        try:
            response = self.chat_session.send_message(full_message, stream=True)
            for chunk in response:
                if chunk.text:
                    yield chunk.text
        except Exception as e:
            yield f"I apologize, but I encountered an error: {str(e)}. Please try again."
    
    def reset_chat(self, system_prompt: str) -> None:
        """
        Reset the chat session with a fresh start
        
        Args:
            system_prompt: The system instruction for the new session
        """
        self.start_chat(system_prompt)


def test_gemini_connection() -> bool:
    """
    Test if Gemini API connection works
    
    Returns:
        True if connection successful, False otherwise
    """
    try:
        client = GeminiClient()
        client.start_chat("You are a helpful assistant. Respond briefly.")
        response = client.generate_response("Say hello in exactly 5 words.")
        return len(response) > 0
    except Exception as e:
        print(f"Gemini connection test failed: {e}")
        return False


if __name__ == "__main__":
    # Test the client
    print("Testing Gemini client...")
    if test_gemini_connection():
        print("✅ Gemini connection successful!")
    else:
        print("❌ Gemini connection failed. Check your API key.")
