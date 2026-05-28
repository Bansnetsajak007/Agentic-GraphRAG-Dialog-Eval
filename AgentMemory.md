# Agent Memory

## Repository

- Workspace: `/mnt/elements/Research/Agentic-GraphRAG-Dialog-Eval`
- Research project: Romanized Nepali customer-support RAG benchmark.
- Current implemented phase: Phase 1 Traditional Semantic RAG baseline only.

## Phase 1 Scope Completed

- Created `pyproject.toml` for a `uv`-managed Python package named `romanized-nepali-ragbench`.
- Added durable project instructions in `AGENTS.md`.
- Added `.env.example` and `.gitignore`.
- Created six ChitoMart synthetic business policy documents under `data/business_docs/`.
- Added documentation under `docs/` for dataset notes, research protocol, and Phase 1 architecture.
- Replaced README with setup and Phase 1 run instructions.

## Implemented Modules

- `src/ragbench/config.py`: environment-backed settings and project paths.
- `src/ragbench/schemas.py`: typed Pydantic schemas for chunks, retrieved context, eval queries, and predictions.
- `src/ragbench/utils/text.py`: deterministic text normalization and chunking helpers.
- `src/ragbench/loaders/document_loader.py`: Markdown document loading and deterministic chunk creation.
- `src/ragbench/loaders/query_loader.py`: raw Crowpeaks CSV preparation and processed eval query loading.
- `src/ragbench/indexing/chroma_index.py`: persistent Chroma indexing with sentence-transformers auto mode and deterministic hash fallback for constrained environments.
- `src/ragbench/retrievers/semantic_retriever.py`: simple top-k semantic retrieval.
- `src/ragbench/llms/chat.py`: Google Gemini and NVIDIA NIM chat wrapper with retrieval-only placeholder when no selected provider key is set.
- `src/ragbench/pipelines/semantic_rag.py`: Traditional Semantic RAG pipeline.
- `src/ragbench/evaluators/prediction_writer.py`: JSONL prediction writer.

## Experiment Scripts

- `experiments/prepare_eval_queries.py`
- `experiments/build_semantic_index.py`
- `experiments/run_semantic_rag.py`

## Tests

- `tests/test_document_loader.py`
- `tests/test_query_loader.py`
- `tests/test_semantic_retriever.py`
- `tests/test_prediction_schema.py`

## Validation State

- `uv run pytest` passes with 10 tests.
- `uv run python experiments/build_semantic_index.py --rebuild` passes and indexes 13 business-document chunks.
- `uv run python experiments/prepare_eval_queries.py --limit 100` passes after the raw Crowpeaks CSV was added.
- `uv run python experiments/run_semantic_rag.py --limit 5 --top-k 4` passes and writes 5 retrieval-only predictions when no Gemini/NVIDIA key is set.
- Previous provider support was removed. Phase 1 now supports only `gemini` and `nvidia`; `LLM_PROVIDER=auto` picks whichever supported API key is present, preferring Gemini over NVIDIA.

## Important Data Assumption

The raw customer-message dataset is expected at:

```text
data/raw/Crowpeaks - label test data - 6K Sample.csv
```

It must contain `Input` and `Output` columns. It should be used only for evaluation queries, not as business knowledge.

## Phase Boundary

Do not add Agentic RAG, GraphRAG, query rewriting, intent routing, verifier agents, graph extraction, graph lookup, reranking, or planning to Phase 1 files. Future phases should be implemented in separate modules while preserving the Phase 1 output schema for fair comparison.
