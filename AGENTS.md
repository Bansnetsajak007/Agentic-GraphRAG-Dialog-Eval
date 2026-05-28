# Project Instructions for Codex Agents

This repository is a research benchmark for Romanized Nepali customer-support retrieval-augmented generation. It is not a production chatbot.

## Scope Control

- Keep baseline systems simple and controlled.
- Phase 1 is only Traditional Semantic RAG.
- Do not mix Phase 2 Agentic RAG behavior into Phase 1.
- Do not mix Phase 3 Agentic GraphRAG behavior into Phase 1.
- Do not add query rewriting, intent routing, verifier agents, graph extraction, or graph lookup to Phase 1 code.

## Reproducibility

- Preserve deterministic data preparation and chunking where possible.
- Always save experiment outputs under `results/`.
- Use explicit CLI arguments for experiment variation.
- Do not silently ignore missing input files.
- Keep output schemas stable so systems can be compared fairly.

## Secrets and Configuration

- Do not hardcode API keys or provider secrets.
- Read LLM provider keys and model names from the environment.
- Supported Phase 1 LLM providers are Google Gemini and NVIDIA NIM only.
- The benchmark must support retrieval-only runs when no LLM API key is available.

## Engineering Style

- Prefer small, testable modules.
- Prefer readable research code over framework-heavy production abstractions.
- Keep dependencies focused on the current phase.
- Add tests for loaders, schemas, retrieval structures, and output writing.
