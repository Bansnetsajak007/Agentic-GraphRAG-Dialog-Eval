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
    repeated_lists: dict[str, list[str]] = {"GEMINI_API_KEYS": []}
    for raw_line in path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        key = key.strip()
        value = value.strip().strip('"').strip("'")
        if key in repeated_lists:
            repeated_lists[key].extend(item.strip() for item in value.split(",") if item.strip())
        elif key and key not in os.environ:
            os.environ[key] = value

    for key, values in repeated_lists.items():
        if values and key not in os.environ:
            os.environ[key] = ",".join(values)


def parse_env_list(name: str) -> list[str]:
    value = os.getenv(name, "")
    return [item.strip() for item in value.split(",") if item.strip()]


class Settings(BaseModel):
    """Environment-backed settings used by scripts and pipelines."""

    project_root: Path = PROJECT_ROOT
    raw_csv_path: Path = PROJECT_ROOT / "data/raw/Crowpeaks - label test data - 6K Sample.csv"
    processed_queries_path: Path = PROJECT_ROOT / "data/processed/eval_queries_v1.csv"
    eval_queries_dir: Path = PROJECT_ROOT / "data/eval/queries"
    evaluation_dataset_path: Path = (
        PROJECT_ROOT / "data/eval/queries/romanized_nepali_rag_eval_queries_300.csv"
    )
    business_docs_dir: Path = PROJECT_ROOT / "data/business_docs"
    chroma_dir: Path = PROJECT_ROOT / ".chroma/semantic_rag"
    predictions_path: Path = PROJECT_ROOT / "results/predictions/semantic_rag_v1.jsonl"
    traditional_rag_results_path: Path = PROJECT_ROOT / "results/traditional_rag/eval_results.jsonl"
    agentic_rag_results_path: Path = PROJECT_ROOT / "results/agentic_rag/eval_results.jsonl"
    agentic_graph_rag_results_path: Path = PROJECT_ROOT / "results/agentic_graph_rag/eval_results.jsonl"
    evaluation_summary_path: Path = PROJECT_ROOT / "results/summary/evaluation_summary.csv"
    company_knowledge_base_map: dict[str, str] = Field(
        default_factory=lambda: {
            "QuickCommerce / E-commerce Company": "chitomart",
            "Hosting / Cloud Provider": "cloudsewa",
            "PaySathi Wallet / FinTech Payment Company": "paysathi",
            "chitomart": "chitomart",
            "cloudsewa": "cloudsewa",
            "paysathi": "paysathi",
        }
    )
    collection_name: str = "phase1_semantic_rag"
    embedding_provider: str = Field(default_factory=lambda: os.getenv("EMBEDDING_PROVIDER", "sentence-transformers").lower())
    embedding_model: str = Field(
        default_factory=lambda: os.getenv(
            "EMBEDDING_MODEL",
            "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2",
        )
    )
    embedding_dimensions: int = Field(default_factory=lambda: int(os.getenv("EMBEDDING_DIMENSIONS", "768")))
    llm_provider: str = Field(default_factory=lambda: os.getenv("LLM_PROVIDER", "auto").lower())
    openai_api_key: str | None = Field(default_factory=lambda: os.getenv("OPENAI_API_KEY"))
    openai_base_url: str = Field(default_factory=lambda: os.getenv("OPENAI_BASE_URL", "https://api.openai.com/v1"))
    openai_model: str = Field(default_factory=lambda: os.getenv("OPENAI_MODEL", "gpt-4o-mini"))
    gemini_api_key: str | None = Field(default_factory=lambda: os.getenv("GEMINI_API_KEY"))
    gemini_api_keys: list[str] = Field(default_factory=lambda: parse_env_list("GEMINI_API_KEYS"))
    gemini_base_url: str = Field(
        default_factory=lambda: os.getenv("GEMINI_BASE_URL", "https://generativelanguage.googleapis.com/v1beta")
    )
    gemini_model: str = Field(default_factory=lambda: os.getenv("GEMINI_MODEL", "gemini-2.5-flash"))
    nvidia_api_key: str | None = Field(default_factory=lambda: os.getenv("NVIDIA_API_KEY"))
    nvidia_base_url: str = Field(default_factory=lambda: os.getenv("NVIDIA_BASE_URL", "https://integrate.api.nvidia.com/v1"))
    nvidia_model: str = Field(default_factory=lambda: os.getenv("NVIDIA_MODEL", "meta/llama-3.1-8b-instruct"))

    @property
    def architecture_results_paths(self) -> dict[str, Path]:
        return {
            "traditional_rag": self.traditional_rag_results_path,
            "agentic_rag": self.agentic_rag_results_path,
            "agentic_graph_rag": self.agentic_graph_rag_results_path,
        }


def get_settings() -> Settings:
    load_dotenv_file(PROJECT_ROOT / ".env")
    return Settings()
