import os
from pydantic_settings import BaseSettings
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()


class Settings(BaseSettings):
    """Application settings"""

    # App settings
    APP_NAME: str = os.getenv("APP_NAME", "Personal Voice Bot")
    APP_ENV: str = os.getenv("APP_ENV", "development")
    DEBUG: bool = os.getenv("DEBUG", "True") == "True"

    # API settings
    API_HOST: str = os.getenv("API_HOST", "0.0.0.0")
    API_PORT: int = int(os.getenv("API_PORT", "8000"))

    # Streamlit settings
    STREAMLIT_SERVER_PORT: int = int(os.getenv("STREAMLIT_SERVER_PORT", "8501"))
    STREAMLIT_SERVER_HEADLESS: bool = (
        os.getenv("STREAMLIT_SERVER_HEADLESS", "True") == "True"
    )

    # OpenAI settings
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "")
    OPENAI_MODEL: str = os.getenv("OPENAI_MODEL", "gpt-4o-mini")

    # Groq settings
    GROQ_API_KEY: str = os.getenv("GROQ_API_KEY", "")
    GROQ_MODEL: str = os.getenv("GROQ_MODEL", "llama3-70b-8192")

    # Model Settings
    CURRENT_MODEL: str = GROQ_MODEL

    # Voice settings
    TTS_LANGUAGE: str = os.getenv("TTS_LANGUAGE", "en")
    TTS_SPEED: float = float(os.getenv("TTS_SPEED", "1.0"))
    STT_LANGUAGE: str = os.getenv("STT_LANGUAGE", "en-US")

    class Config:
        case_sensitive = True


# Create settings instance
settings = Settings()
