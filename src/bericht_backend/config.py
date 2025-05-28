"""Configuration module for the Transcribo backend.

This module loads configuration values from environment variables.
"""

import os

from dotenv import load_dotenv
from llm_facade.llm_config import LLMConfig
from pydantic import Field


class Configuration(LLMConfig):
    """Application settings loaded from environment variables."""

    whisper_api: str = Field(title="Whisper API URL")

    @classmethod
    def from_env(cls) -> "Configuration":
        """Create settings from environment variables.

        Returns:
            Settings: Application settings object

        Raises:
            ValueError: If a required environment variable is missing
        """
        load_dotenv()  # Load .env file if present

        whisper_api = os.getenv("WHISPER_API", "")
        llm_api = os.getenv("LLM_API", "")
        llm_api_key = os.getenv("LLM_API_KEY", "")
        llm_model = os.getenv("LLM_MODEL", "cortecs/Llama-3.3-70B-Instruct-FP8-Dynamic")

        return cls(
            whisper_api=whisper_api, openai_api_base_url=llm_api, openai_api_key=llm_api_key, llm_model=llm_model
        )
