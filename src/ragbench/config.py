"""Runtime configuration for the benchmark."""

from __future__ import annotations

import os
from pathlib import Path

from pydantic import BaseModel, Field


PROJECT_ROOT = Path(__file__).resolve().parents[2]


def load_dotenv_file(path: Path) -> None:
    """Load simple KEY=VALUE lines from .env without overriding exported env vars."""

    if not path.exists():
        return
    for raw_line in path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        key = key.strip()
        value = value.strip().strip('"').strip("'")
        if key and key not in os.environ:
            os.environ[key] = value


class Settings(BaseModel):
    """Environment-backed settings used by scripts and pipelines."""

    project_root: Path = PROJECT_ROOT
    raw_csv_path: Path = PROJECT_ROOT / "data/raw/Crowpeaks - label test data - 6K Sample.csv"
    processed_queries_path: Path = PROJECT_ROOT / "data/processed/eval_queries_v1.csv"
    business_docs_dir: Path = PROJECT_ROOT / "data/business_docs"
    chroma_dir: Path = PROJECT_ROOT / ".chroma/semantic_rag"
    predictions_path: Path = PROJECT_ROOT / "results/predictions/semantic_rag_v1.jsonl"
    collection_name: str = "chitomart_phase1_semantic_rag"
    embedding_model: str = Field(
        default_factory=lambda: os.getenv(
            "EMBEDDING_MODEL",
            "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2",
        )
    )
    llm_provider: str = Field(default_factory=lambda: os.getenv("LLM_PROVIDER", "auto").lower())
    gemini_api_key: str | None = Field(default_factory=lambda: os.getenv("GEMINI_API_KEY"))
    gemini_base_url: str = Field(
        default_factory=lambda: os.getenv("GEMINI_BASE_URL", "https://generativelanguage.googleapis.com/v1beta")
    )
    gemini_model: str = Field(default_factory=lambda: os.getenv("GEMINI_MODEL", "gemini-2.5-flash"))
    nvidia_api_key: str | None = Field(default_factory=lambda: os.getenv("NVIDIA_API_KEY"))
    nvidia_base_url: str = Field(default_factory=lambda: os.getenv("NVIDIA_BASE_URL", "https://integrate.api.nvidia.com/v1"))
    nvidia_model: str = Field(default_factory=lambda: os.getenv("NVIDIA_MODEL", "meta/llama-3.1-8b-instruct"))


def get_settings() -> Settings:
    load_dotenv_file(PROJECT_ROOT / ".env")
    return Settings()
