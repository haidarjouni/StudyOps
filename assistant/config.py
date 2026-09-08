import os
from dataclasses import dataclass
from urllib.parse import quote

from dotenv import load_dotenv

load_dotenv()  # Load environment variables from .env file


@dataclass(frozen=True)
class Config:
    @property
    def checkpoint_database_url(self) -> str:
        user = quote(os.environ["POSTGRES_USER"], safe="")
        password = quote(os.environ["POSTGRES_PASSWORD"], safe="")
        database = quote(os.environ["POSTGRES_DB"], safe="")
        host = os.environ.get("POSTGRES_HOST", "localhost")
        port = os.environ.get("POSTGRES_PORT", os.environ.get("DB_HOST_PORT", "5432"))
        return f"postgresql://{user}:{password}@{host}:{port}/{database}"

    # ChatOpenAI reads OPENAI_API_KEY directly from the environment.
    openai_model: str = os.environ.get("OPENAI_MODEL", "gpt-5.6-terra")

    # The base URL of the DRF API.
    base_drf_api: str = os.environ.get("BASE_DRF_API", "http://localhost:8000/api/")

    langsmith_api_key: str = os.environ.get("LANGSMITH_API_KEY", "")
    langsmith_endpoint: str = os.environ.get(
        "LANGSMITH_ENDPOINT", "https://api.smith.langchain.com"
    )
    langsmith_project: str = os.environ.get("LANGSMITH_PROJECT", "studyops")
