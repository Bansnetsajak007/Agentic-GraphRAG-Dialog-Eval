# Agentic-GraphRAG-Dialog-Eval

A controlled, comparative evaluation of three retrieval-based chatbot architectures for **Romanized Nepali customer-support dialogue**. This project aims to identify which architecture performs best across different types of user queries, rather than claiming a single “best” solution.

Prepared for submission to **WOCHAT 2026**.

## Overview
Customer support chats in Romanized Nepali are messy—mixing Nepali and English, slang, abbreviations, and frequent typos. A fluent chatbot is not enough; it must provide answers grounded in actual business rules (delivery, refunds, payments) without hallucinating policies.

This repository will run **the same dataset** and **the same knowledge base** through three different retrieval architectures to fairly evaluate correctness, faithfulness, robustness, latency, and cost.

## Architectures evaluated
To ensure a fair comparison, the base LLM, embedding model, business documents, and evaluation rubric remain constant. Only the retrieval/control architecture changes.

| Architecture | Pipeline highlights | Expected strength |
|---|---|---|
| Traditional Semantic RAG | User query → embedding search → top-k chunks → LLM answer | Fast, simple, and cheap. Ideal for direct FAQ-style questions. |
| Agentic RAG | Intent detection → reformulation → retrieval → verification → answer | Stronger intent handling and clarification for ambiguous or noisy queries. |
| Agentic GraphRAG | Entity/relation graph → agentic graph/semantic lookup → answer | Excels at multi-hop reasoning, policy relationships, and area-based rules. |

## Dataset & benchmarks
The evaluation relies on a custom benchmark of **60–100 realistic Romanized Nepali customer-support questions**, categorized to test specific system capabilities:

- **Simple factual:** direct retrieval (e.g., “delivery charge kati ho?”)
- **Policy-based:** hallucination control (e.g., “damaged product aayo vane refund huncha?”)
- **Multi-hop:** rule combination (e.g., “Baneshwor ma Rs.1500 ko order garda free delivery huncha?”)
- **Ambiguous:** intent detection (e.g., “mero order bigriyo aba k garne?”)
- **Code-mixed:** Nepali-English understanding (e.g., “payment failed vayo but paisa katyo what should I do?”)
- **Noisy/typo:** robustness to spelling (e.g., “dilivery kati lagxa ktm ma?”)
- **Complaint tone:** helpful and respectful tone (e.g., “timi haru le wrong item pathayau”)

## Evaluation metrics
Outputs are evaluated using a mix of human scoring (1–5 scale) and automated metrics.

Qualitative (human-scored):
- Answer correctness (matches business rules)
- Faithfulness (grounded in retrieved evidence)
- Helpfulness (solves the customer’s problem)
- Romanized Nepali naturalness
- Robustness (handling typos, slang, and mixed language)
- Clarification behavior (asks for missing info when needed)

Quantitative (automated):
- Latency (average response time in seconds)
- Cost (token usage and model-call count per query)

## Quick start (development workflow)
This project is structured as a 7-day sprint:

1. Day 1–2: finalize domain and create the business knowledge base (documents) + dataset queries
2. Day 3: implement Traditional Semantic RAG baseline and logging format
3. Day 4: implement Agentic RAG workflow
4. Day 5: implement Agentic GraphRAG workflow
5. Day 6: run experiments, score outputs, and collect latency/cost data
6. Day 7: analyze results and draft the 4-page short paper

(Code execution and environment setup instructions will be added once the baseline implementation is complete.)

## References
- WOCHAT 2026 CFP: Workshop on Chatbots and Agentic Technologies.
- Lewis et al. (2020). *Retrieval-Augmented Generation for Knowledge-Intensive NLP Tasks.*
- Edge et al. (2024). *From Local to Global: A Graph RAG Approach to Query-Focused Summarization.*
- Singh et al. (2025). *Agentic Retrieval-Augmented Generation: A Survey on Agentic RAG.*
