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

## Components

- Business knowledge: `data/business_docs/**/*.md`
- Raw customer-message dataset: `data/raw/Crowpeaks - label test data - 6K Sample.csv`
- Prepared evaluation queries: `data/processed/eval_queries_v1.csv`
- Romanized Nepali RAG evaluation dataset: `data/eval/queries/romanized_nepali_rag_eval_queries_300.csv`
- Chroma vector index: `.chroma/semantic_rag`
- Predictions: `results/predictions/semantic_rag_v1.jsonl`
- Architecture evaluation outputs:
  - `results/traditional_rag/eval_results.jsonl`
  - `results/agentic_rag/eval_results.jsonl`
  - `results/agentic_graph_rag/eval_results.jsonl`
  - `results/summary/evaluation_summary.csv`

The raw Crowpeaks CSV is used only as a source of evaluation queries. It is not used as a knowledge base. Business corpora are organized by company, for example `data/business_docs/chitomart/`.

## Setup

Install `uv`, then run commands from the repository root.

```bash
uv sync --dev
cp .env.example .env
```

Environment variables:

```bash
LLM_PROVIDER=openai
OPENAI_API_KEY=
OPENAI_BASE_URL=https://api.openai.com/v1
OPENAI_MODEL=gpt-4o-mini
GEMINI_API_KEY=
GEMINI_API_KEYS=
GEMINI_BASE_URL=https://generativelanguage.googleapis.com/v1beta
GEMINI_MODEL=gemini-2.5-flash
NVIDIA_API_KEY=
NVIDIA_BASE_URL=https://integrate.api.nvidia.com/v1
NVIDIA_MODEL=meta/llama-3.1-8b-instruct
EMBEDDING_PROVIDER=gemini
EMBEDDING_MODEL=gemini-embedding-2
EMBEDDING_DIMENSIONS=768
```

For OpenAI answer generation with Gemini embeddings, set `LLM_PROVIDER=openai`, `OPENAI_API_KEY`, `EMBEDDING_PROVIDER=gemini`, `EMBEDDING_MODEL=gemini-embedding-2`, and `GEMINI_API_KEY` or `GEMINI_API_KEYS`. Rebuild the Chroma index after changing `EMBEDDING_PROVIDER`, `EMBEDDING_MODEL`, or `EMBEDDING_DIMENSIONS`.

`LLM_PROVIDER` can be `auto`, `openai`, `gemini`, or `nvidia`. In `auto` mode, the runner chooses OpenAI when `OPENAI_API_KEY` is set, Gemini when `GEMINI_API_KEY` or `GEMINI_API_KEYS` is set, otherwise NVIDIA when `NVIDIA_API_KEY` is set. `GEMINI_API_KEYS` accepts a comma-separated list; Gemini requests choose a key randomly and switch keys again on 429/503 responses. API keys are optional for retrieval-only testing; if no supported key is set, the benchmark still runs retrieval and writes predictions with a generation-skipped placeholder answer.

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

## Run Architecture Evaluation

Place the 300-query Romanized Nepali RAG evaluation CSV here:

```text
data/eval/queries/romanized_nepali_rag_eval_queries_300.csv
```

The loader validates `query_id`, `company`, `difficulty`, a query column (`query` or `query_romanized`), and a category column (`category` or `query_type`). If `expected_document` or `expected_topic` are present, they are copied into the result records. The included dataset uses `topic` as the expected topic.

Build the company indexes before running evaluation:

```bash
uv run python experiments/build_semantic_index.py --rebuild
```

Run each architecture:

```bash
uv run python -m ragbench.evaluators.run_eval --architecture traditional_rag
uv run python -m ragbench.evaluators.run_eval --architecture agentic_rag
uv run python -m ragbench.evaluators.run_eval --architecture agentic_graph_rag
```

Useful options:

```bash
uv run python -m ragbench.evaluators.run_eval --architecture traditional_rag --limit 20 --top-k 4
uv run python -m ragbench.evaluators.run_eval --architecture traditional_rag --resume
```

The runner maps dataset company labels to knowledge-base folders:

```text
QuickCommerce / E-commerce Company -> data/business_docs/chitomart/
Hosting / Cloud Provider -> data/business_docs/cloudsewa/
PaySathi Wallet / FinTech Payment Company -> data/business_docs/paysathi/
```

Per-query failures are written into the JSONL `error` field so completed queries remain available for analysis. A summary CSV is refreshed at `results/summary/evaluation_summary.csv` after each run.

## Run Research-Grade RAG Metrics

After architecture outputs exist under `results/{architecture}/eval_results.jsonl`, compute retrieval, generation, Romanized Nepali robustness, and operational metrics:

```bash
uv run python -m ragbench.evaluators.run_all \
  --dataset data/eval/romanized_nepali_rag_eval_queries_300.csv \
  --results-dir results
```

For long LLM-as-judge runs, use checkpoint/resume mode:

```bash
uv run python -m ragbench.evaluators.run_all \
  --dataset data/eval/romanized_nepali_rag_eval_queries_300.csv \
  --results-dir results \
  --judge-provider openai \
  --judge-model gpt-5.2 \
  --resume-detailed
```

Outputs:

```text
results/traditional_rag/rag_metrics_detailed.jsonl
results/agentic_rag/rag_metrics_detailed.jsonl
results/agentic_graph_rag/rag_metrics_detailed.jsonl
results/rag_evaluation_summary.csv
results/rag_evaluation_summary.json
results/rag_evaluation_by_company.csv
results/rag_evaluation_by_difficulty.csv
results/rag_evaluation_report.md
```

The evaluator uses deterministic scoring where possible: retrieval hit/ranking metrics from expected topic/source metadata, company-domain accuracy, intent/category accuracy, retrieved chunk counts, latency percentiles, and success/failure rates.

LLM-as-judge scoring is optional and disabled by default. To enable it, set judge-specific environment variables:

```bash
JUDGE_LLM_PROVIDER=openai
JUDGE_OPENAI_API_KEY=
JUDGE_OPENAI_MODEL=gpt-4o-mini
```

Supported judge providers are `openai`, `gemini`, and `nvidia`; `JUDGE_LLM_PROVIDER=auto` reuses the available provider keys. Judge-dependent fields remain blank when no judge is configured.

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
