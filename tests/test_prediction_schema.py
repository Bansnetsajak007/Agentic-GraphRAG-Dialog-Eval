import json
from pathlib import Path

from ragbench.evaluators.prediction_writer import write_predictions
from ragbench.schemas import Prediction, RetrievedChunk


def test_prediction_schema_and_jsonl_writer(tmp_path: Path) -> None:
    prediction = Prediction(
        id="Q0001",
        query="delivery charge kati ho?",
        intent="Inquiry",
        retrieved_context=[
            RetrievedChunk(
                chunk_id="delivery_policy-001",
                source="delivery_policy.md",
                content="Delivery charge is NPR 60.",
                score=0.2,
            )
        ],
        answer="Kathmandu Ring Road bhitra delivery charge NPR 60 ho.",
        latency_ms=123,
        metadata={"top_k": 4, "embedding_model": "fake", "llm_model": "fake"},
    )
    output_path = tmp_path / "predictions.jsonl"

    count = write_predictions([prediction], output_path)

    assert count == 1
    line = output_path.read_text(encoding="utf-8").strip()
    payload = json.loads(line)
    assert payload["id"] == "Q0001"
    assert payload["system"] == "semantic_rag"
    assert payload["retrieved_context"][0]["source"] == "delivery_policy.md"
