import os
from pathlib import Path

from ragbench.config import load_dotenv_file


def test_load_dotenv_file_merges_repeated_gemini_key_lists(tmp_path: Path, monkeypatch) -> None:
    monkeypatch.delenv("GEMINI_API_KEYS", raising=False)
    env_path = tmp_path / ".env"
    env_path.write_text(
        "\n".join(
            [
                "GEMINI_API_KEYS=key-a",
                "GEMINI_API_KEYS=key-b,key-c",
                "GEMINI_API_KEYS=key-d",
            ]
        ),
        encoding="utf-8",
    )

    load_dotenv_file(env_path)

    assert os.environ["GEMINI_API_KEYS"] == "key-a,key-b,key-c,key-d"
