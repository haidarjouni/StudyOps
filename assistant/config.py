from dataclasses import dataclass
import os
from dotenv import load_dotenv

load_dotenv()  # Load environment variables from .env file


@dataclass(frozen=True)
class Config:
    # The URL of the Ollama API.
    ollama_url: str = os.environ.get("OLLAMA_URL", "http://localhost:11434")

    # The base URL of the DRF API.
    base_drf_api: str = os.environ.get("BASE_DRF_API", "http://localhost:8000/api/")
