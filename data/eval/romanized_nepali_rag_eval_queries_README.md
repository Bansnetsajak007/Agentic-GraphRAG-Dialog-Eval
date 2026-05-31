# Romanized Nepali RAG Evaluation Query Set

This dataset contains 300 synthetic customer-support evaluation queries for comparing three RAG architectures over Romanized Nepali support dialogues.

## Companies
- QuickCommerce / E-commerce Company: 100 queries
- Hosting / Cloud Provider: 100 queries
- PaySathi Wallet / FinTech Payment Company: 100 queries

## Difficulty distribution
Each company contains:
- 40 simple fact-lookup queries
- 30 medium procedural queries
- 30 complex multi-hop or adversarial edge-case queries

## Fields
- `query_id`: Stable query identifier.
- `company`: Company/domain bucket.
- `topic`: Policy/support area expected to be retrieved.
- `difficulty`: simple, medium, or complex.
- `query_type`: fact_lookup, procedural, multi_hop, or adversarial_edge_case.
- `language_style`: romanized_nepali_mixed_english.
- `query_romanized`: The customer query to run against each RAG architecture.

## Suggested use
Run the same 300 queries against Traditional Semantic RAG, Agentic RAG, and Agentic Graph RAG. Capture retrieved chunk IDs, generated answer, latency, token cost, and failure category. For stronger research quality, add human-written gold answers and expected document/chunk IDs before final scoring.
