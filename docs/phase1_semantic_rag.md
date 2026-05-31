# Phase 1: Traditional Semantic RAG

## Architecture

The Phase 1 baseline follows a classic semantic RAG flow:

```text
customer query -> embed query -> Chroma vector search -> top-k chunks -> grounded answer -> JSONL prediction
```

## Modules

- `src/ragbench/loaders/document_loader.py`: loads and chunks Markdown business documents.
- `src/ragbench/loaders/query_loader.py`: prepares and reads evaluation query CSV files.
- `src/ragbench/indexing/chroma_index.py`: builds the persistent Chroma index.
- `src/ragbench/retrievers/semantic_retriever.py`: retrieves top-k chunks with semantic search.
- `src/ragbench/llms/chat.py`: calls Google Gemini or NVIDIA NIM when configured.
- `src/ragbench/pipelines/semantic_rag.py`: runs retrieval and answer generation.
- `src/ragbench/evaluators/prediction_writer.py`: writes JSONL predictions.

## Inputs

- Raw customer messages: `data/raw/Crowpeaks - label test data - 6K Sample.csv`
- Processed evaluation queries: `data/processed/eval_queries_v1.csv`
- Business documents: `data/business_docs/**/*.md`

## Outputs

- Chroma index: `.chroma/semantic_rag`
- Predictions: `results/predictions/semantic_rag_v1.jsonl`

## Intentionally Excluded

Phase 1 does not include query rewriting, intent routing, agent planning, verifier agents, graph extraction, graph traversal, or reranking.

## Role in Later Comparison

This baseline provides the simple retrieval-only control system. Phase 2 and Phase 3 should be compared against it using the same evaluation queries, business documents, and output schema.
