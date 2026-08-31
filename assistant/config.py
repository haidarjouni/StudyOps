import os
from dataclasses import dataclass

from dotenv import load_dotenv

load_dotenv()  # Load environment variables from .env file


@dataclass(frozen=True)
class Config:
    # The URL of the Ollama API.
    ollama_url: str = os.environ.get("OLLAMA_URL", "http://localhost:11434")

    # The base URL of the DRF API.
    base_drf_api: str = os.environ.get("BASE_DRF_API", "http://localhost:8000/api/")

    langsmith_api_key: str = os.environ.get("LANGSMITH_API_KEY", "")
    langsmith_endpoint: str = os.environ.get(
        "LANGSMITH_ENDPOINT", "https://api.smith.langchain.com"
    )
    langsmith_project: str = os.environ.get("LANGSMITH_PROJECT", "studyops")
