# Research Protocol

This benchmark compares retrieval-augmented generation architectures on the same Romanized Nepali customer-support task.

## Controlled Inputs

- Same evaluation query set
- Same ChitoMart business document corpus
- Same embedding model unless explicitly documented
- Same answer output schema
- Same evaluation rubric in later phases

## Systems

1. Traditional Semantic RAG
2. Agentic RAG
3. Agentic GraphRAG

Phase 1 implements only Traditional Semantic RAG. Later phases should add capabilities in separate modules while preserving comparable inputs and outputs.

## Output Discipline

All benchmark runs must save predictions under `results/predictions/` and include retrieved context, latency, model metadata, and system name.
