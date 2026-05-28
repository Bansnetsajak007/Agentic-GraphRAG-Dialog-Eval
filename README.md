# Agentic-GraphRAG-Dialog-Eval

Research benchmark for comparing retrieval-augmented generation architectures on **Romanized Nepali customer-support dialogue**. The repository currently implements **Phase 1: Traditional Semantic RAG** as a controlled baseline.

Prepared for submission to **WOCHAT 2026**.

## Project Goal

The benchmark compares three systems on the same customer queries and ChitoMart business policy corpus:

1. Traditional Semantic RAG
2. Agentic RAG
3. Agentic GraphRAG

Phase 1 implements only the first system:

```text
customer query -> embed query -> semantic vector search -> retrieve top-k chunks -> grounded answer -> JSONL prediction
```

Agentic RAG and Agentic GraphRAG are future phases and are intentionally excluded from the current baseline.

## Phase 1 Components

- Business knowledge: `data/business_docs/*.md`
- Raw customer-message dataset: `data/raw/Crowpeaks - label test data - 6K Sample.csv`
- Prepared evaluation queries: `data/processed/eval_queries_v1.csv`
- Chroma vector index: `.chroma/semantic_rag`
- Predictions: `results/predictions/semantic_rag_v1.jsonl`

The raw Crowpeaks CSV is used only as a source of evaluation queries. It is not used as a knowledge base.

## Setup

Install `uv`, then run commands from the repository root.

```bash
uv sync --dev
cp .env.example .env
```

Environment variables:

```bash
LLM_PROVIDER=auto
GEMINI_API_KEY=
GEMINI_BASE_URL=https://generativelanguage.googleapis.com/v1beta
GEMINI_MODEL=gemini-2.5-flash
NVIDIA_API_KEY=
NVIDIA_BASE_URL=https://integrate.api.nvidia.com/v1
NVIDIA_MODEL=meta/llama-3.1-8b-instruct
EMBEDDING_MODEL=sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2
```

`LLM_PROVIDER` can be `auto`, `gemini`, or `nvidia`. In `auto` mode, the runner chooses Gemini when `GEMINI_API_KEY` is set, otherwise NVIDIA when `NVIDIA_API_KEY` is set. API keys are optional for retrieval-only testing; if no supported key is set, the benchmark still runs retrieval and writes predictions with a generation-skipped placeholder answer.

## Run Phase 1

Place the raw dataset here:

```text
data/raw/Crowpeaks - label test data - 6K Sample.csv
```

Prepare evaluation queries:

```bash
uv run python experiments/prepare_eval_queries.py --limit 100
```

Build or rebuild the semantic Chroma index:

```bash
uv run python experiments/build_semantic_index.py --rebuild
```

Run the Traditional Semantic RAG baseline:

```bash
uv run python experiments/run_semantic_rag.py --limit 20 --top-k 4
```

Run tests:

```bash
uv run pytest
```

## Output Format

Predictions are JSONL records with the stable schema:

```json
{
  "id": "Q0001",
  "system": "semantic_rag",
  "query": "...",
  "intent": "...",
  "retrieved_context": [
    {
      "chunk_id": "...",
      "source": "...",
      "content": "...",
      "score": 0.123
    }
  ],
  "answer": "...",
  "latency_ms": 1234,
  "metadata": {
    "top_k": 4,
    "embedding_model": "...",
    "embedding_backend": "...",
    "llm_model": "...",
    "llm_provider": "..."
  }
}
```

## Phase Boundaries

Phase 1 does not implement query rewriting, intent routing, verifier agents, graph extraction, graph traversal, reranking, or planning. Keeping this baseline simple makes later comparison against Agentic RAG and Agentic GraphRAG fair.
