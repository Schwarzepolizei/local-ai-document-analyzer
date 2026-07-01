from pathlib import Path

from pydantic import BaseModel


class Settings(BaseModel):
    project_root: Path = Path(__file__).resolve().parents[2]
    data_dir: Path = project_root / "data"
    logs_dir: Path = project_root / "logs"

    app_name: str = "Local AI Document Analyzer"
    app_version: str = "0.1.0"

    ollama_base_url: str = "http://localhost:11434"
    default_llm_model: str = "qwen2.5:7b-instruct"

    embedding_model: str = "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"


settings = Settings()
