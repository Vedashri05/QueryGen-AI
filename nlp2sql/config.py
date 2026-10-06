import os
from dataclasses import dataclass

from dotenv import load_dotenv

load_dotenv()


@dataclass(frozen=True)
class Settings:
    provider: str = os.getenv("LLM_PROVIDER", "anthropic").lower()
    db_url: str = os.getenv("DB_URL", "sqlite:///data/sample.db")

    anthropic_key: str = os.getenv("ANTHROPIC_API_KEY", "")
    anthropic_model: str = os.getenv("ANTHROPIC_MODEL", "claude-sonnet-4-6")

    openai_key: str = os.getenv("OPENAI_API_KEY", "")
    openai_model: str = os.getenv("OPENAI_MODEL", "gpt-4o-mini")

    gemini_key: str = os.getenv("GEMINI_API_KEY", "")
    gemini_model: str = os.getenv("GEMINI_MODEL", "gemini-flash-latest")

    groq_key: str = os.getenv("GROQ_API_KEY", "")
    groq_model: str = os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile")

    ollama_url: str = os.getenv("OLLAMA_URL", "http://localhost:11434/v1")
    ollama_model: str = os.getenv("OLLAMA_MODEL", "llama3.1")

    azure_key: str = os.getenv("AZURE_OPENAI_API_KEY", "")
    azure_endpoint: str = os.getenv("AZURE_OPENAI_ENDPOINT", "")
    azure_version: str = os.getenv("AZURE_OPENAI_API_VERSION", "2024-06-01")
    azure_deployment: str = os.getenv("AZURE_OPENAI_DEPLOYMENT", "")


settings = Settings()
