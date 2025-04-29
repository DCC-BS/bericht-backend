"""Configuration module for the Transcribo backend.

This module loads configuration values from environment variables.
"""

import os

from dotenv import load_dotenv
from pydantic import BaseModel, Field


class Settings(BaseModel):
    """Application settings loaded from environment variables."""

    whisper_api: str = Field(title="Whisper API URL")
    llm_api: str = Field(title="LLM API URL")
    llm_api_key: str = Field(title="LLM API Key", default='')
    llm_model: str = Field(title="LLM Model", default='cortecs/Llama-3.3-70B-Instruct-FP8-Dynamic')

    @classmethod
    def from_env(cls) -> "Settings":
        """Create settings from environment variables.

        Returns:
            Settings: Application settings object

        Raises:
            ValueError: If a required environment variable is missing
        """
        load_dotenv()  # Load .env file if present

        whisper_api = os.getenv("WHISPER_API", '')
        llm_api = os.getenv("LLM_API", '')
        llm_api_key = os.getenv("LLM_API_KEY", '')
        llm_model = os.getenv("LLM_MODEL", 'cortecs/Llama-3.3-70B-Instruct-FP8-Dynamic')

        return cls(whisper_api=whisper_api, llm_api=llm_api, llm_api_key=llm_api_key, llm_model=llm_model)


# Create a global settings instance for easy import
settings = Settings.from_env()
