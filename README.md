# Agentic GraphRAG Dialog Eval

A research-oriented evaluation project for comparing three Retrieval-Augmented Generation (RAG) architectures on a **Romanized Nepali customer-support assistant** benchmark.

The project evaluates how well different RAG designs answer realistic customer-support queries written in Romanized Nepali, code-mixed Nepali-English, informal spelling, and support-ticket style language across three company domains:

1. **Quick-commerce / E-commerce**  
   Delivery, cancellation, wrong item, refund, return, product availability, order issues.

2. **Hosting / Cloud Provider**  
   Server downtime, VPS, DNS, SSL, domain, billing, SLA, support tickets, hosting reliability.

3. **FinTech / Digital Wallet / Payment Company**  
   Failed payments, money deducted but not received, KYC, refunds, merchant disputes, wallet limits, transaction verification.

---

## Research Objective

The main goal of this project is to study whether more advanced RAG architectures improve answer quality for a Romanized Nepali customer-support agent when all systems are tested on the same internal knowledge base and the same evaluation dataset.

The project compares:

| Architecture | Description |
|---|---|
| `traditional_rag` | Standard retrieve-then-generate RAG baseline. |
| `agentic_rag` | Agentic RAG pipeline with reasoning-oriented query handling before answer generation. |
| `agentic_graph_rag` | Agentic GraphRAG-style pipeline that combines agentic reasoning with graph-aware retrieval / relationship-aware context use. |

---

## Why Romanized Nepali?

Many Nepali users do not type customer-support questions in formal Nepali script. They often use Romanized Nepali such as:

```text
mero payment deduct bhayo tara receiver le paisa paayena
order cancel garepachi refund kati din ma aaucha?
mero vps down cha, SLA claim garna milcha?
```

This makes the task harder than normal English-only support QA because the system must handle:

- Romanized Nepali spelling variation
- Nepali-English code mixing
- Informal support language
- Ambiguous intent
- Domain-specific company policies
- Retrieval from structured and semi-structured internal documents

---

## Dataset

The evaluation dataset contains **300 Romanized Nepali customer-support queries**.

| Company Domain | Query Count |
|---|---:|
| Quick-commerce / E-commerce | 100 |
| Hosting / Cloud Provider | 100 |
| FinTech / Digital Wallet | 100 |
| **Total** | **300** |

The dataset includes simple, medium, and complex queries so that the systems can be tested across different difficulty levels.

Dataset path:

```bash
data/eval/romanized_nepali_rag_eval_queries_300.csv
```

Recommended fields:

```text
query_id, company, difficulty, category, query
```

---

## Knowledge Base

The project uses simulated internal company policy documents for three company types.

These documents cover realistic customer-support topics such as:

- Delivery policy
- Refund and cancellation policy
- Wrong item and return handling
- Product availability
- Server downtime and SLA policy
- VPS and hosting billing
- DNS, SSL, and domain support
- Failed wallet payments
- KYC verification
- Merchant disputes
- Wallet limits
- Transaction verification

The knowledge base is intentionally multi-domain so that the RAG pipelines must retrieve the correct policy context before generating the answer.

---

## Evaluation Methodology

The evaluation has two layers:

### 1. System-level execution metrics

These measure whether the RAG pipelines successfully answered all queries and how expensive / slow they were.

Tracked fields include:

- Total queries
- Successful queries
- Failed queries
- Average latency in milliseconds
- Average retrieved chunks

### 2. LLM-as-judge quality metrics

A judge model evaluates generated answers across research-style RAG quality dimensions.

The latest completed run used:

```text
Judge provider: OpenAI
Judge model: gpt-5.2
Total judged evaluations: 900
Judge errors: 0
```

That means:

```text
300 queries × 3 architectures = 900 judged outputs
```

---

## Evaluation Metrics

The project uses a combination of retrieval, generation, domain, and operational metrics.

### Retrieval Quality Metrics

| Metric | Purpose |
|---|---|
| `context_precision` | Checks whether the retrieved chunks are relevant and well ranked. |
| `context_recall` | Checks whether the retrieved context contains enough information needed to answer. |
| `context_relevancy` | Checks whether retrieved context is actually useful for the query. |
| `retrieval_quality_score` | Aggregated retrieval-side quality score. |

### Generation Quality Metrics

| Metric | Purpose |
|---|---|
| `faithfulness` | Checks whether the answer is grounded in the retrieved context. |
| `answer_relevancy` | Checks whether the generated answer directly answers the user query. |
| `answer_completeness` | Checks whether the answer covers the required policy details. |
| `answer_correctness` | Checks whether the answer is correct according to the internal knowledge base. |
| `hallucination_risk` | Penalizes unsupported or invented claims. |
| `generation_quality_score` | Aggregated generation-side quality score. |

### Romanized Nepali and Support-Agent Metrics

| Metric | Purpose |
|---|---|
| `romanized_understanding` | Checks whether the system understands Romanized Nepali / code-mixed queries. |
| `intent_understanding` | Checks whether the support intent is correctly understood. |
| `policy_compliance` | Checks whether the answer follows company policy. |
| `escalation_correctness` | Checks whether the answer escalates correctly when needed. |
| `support_tone` | Checks whether the answer sounds helpful and professional. |
| `romanized_robustness_score` | Aggregated Romanized Nepali handling score. |

### Operational Metrics

| Metric | Purpose |
|---|---|
| `latency_ms` | Measures response time per query. |
| `average_latency_ms` | Average response time per architecture. |
| `retrieved_chunks` | Number of chunks retrieved for each query. |
| `average_retrieved_chunks` | Average retrieved chunks per architecture. |
| `success_rate` | Percentage of queries completed without execution failure. |

---

## Current Evaluation Results

### System Execution Summary

| Architecture | Total Queries | Successful | Failed | Avg Latency (ms) | Avg Retrieved Chunks |
|---|---:|---:|---:|---:|---:|
| `traditional_rag` | 300 | 300 | 0 | 2524.2 | 4.0 |
| `agentic_rag` | 300 | 300 | 0 | 2637.4 | 4.0 |
| `agentic_graph_rag` | 300 | 300 | 0 | 3099.4 | 4.0 |

All three systems completed the full benchmark without runtime failures.

---

### LLM-as-Judge Overall Scores

| Rank | Architecture | Overall Score |
|---:|---|---:|
| 1 | `agentic_graph_rag` | 0.7899 |
| 2 | `agentic_rag` | 0.7894 |
| 3 | `traditional_rag` | 0.7886 |

The latest judged run shows `agentic_graph_rag` slightly ahead overall, followed very closely by `agentic_rag` and `traditional_rag`.

Important interpretation:

The score gap is small. The result should be treated as a directional research finding, not a final absolute conclusion. For a stronger research paper, confidence intervals, significance testing, and human evaluation should be added.

---

## Result Interpretation

The current experiment shows that advanced architectures can improve judged answer quality slightly, but the margin is very small.

From an engineering perspective:

- `traditional_rag` is the fastest system.
- `agentic_rag` adds a small latency cost.
- `agentic_graph_rag` achieves the highest judged score but has the highest latency.
- All systems retrieved an average of 4 chunks, so retrieval depth was controlled across architectures.
- Since the final scores are very close, deeper error analysis is more important than only looking at the overall score.

This makes the project useful as a controlled comparative RAG study rather than just a chatbot demo.

---

## Generated Results

The full evaluation run generated the following files:

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

Detailed JSONL files contain per-query metric scores and judge explanations.

Summary CSV / JSON files contain architecture-level, company-level, and difficulty-level comparisons.

---

## Repository Structure

```text
Agentic-GraphRAG-Dialog-Eval/
├── data/
│   ├── eval/
│   │   └── romanized_nepali_rag_eval_queries_300.csv
│   └── knowledge_base/
│       ├── ecommerce/
│       ├── hosting/
│       └── fintech/
├── ragbench/
│   ├── architectures/
│   │   ├── traditional_rag.py
│   │   ├── agentic_rag.py
│   │   └── agentic_graph_rag.py
│   ├── evaluators/
│   │   ├── run_all.py
│   │   ├── judge.py
│   │   └── metrics.py
│   ├── retrieval/
│   ├── generation/
│   └── utils/
├── results/
│   ├── traditional_rag/
│   ├── agentic_rag/
│   ├── agentic_graph_rag/
│   ├── rag_evaluation_summary.csv
│   ├── rag_evaluation_summary.json
│   ├── rag_evaluation_by_company.csv
│   ├── rag_evaluation_by_difficulty.csv
│   └── rag_evaluation_report.md
├── tests/
├── .env.example
├── pyproject.toml
└── README.md
```

Actual folder names may differ slightly depending on local implementation, but this is the intended project organization.

---

## Setup

### 1. Clone the repository

```bash
git clone <your-repo-url>
cd Agentic-GraphRAG-Dialog-Eval
```

### 2. Install dependencies

This project uses `uv` for Python dependency management.

```bash
uv sync
```

### 3. Configure environment variables

Create a `.env` file:

```bash
cp .env.example .env
```

Add your judge model API key:

```env
OPENAI_API_KEY=your_openai_api_key_here
```

Never commit `.env` to GitHub.

---

## Running the Evaluation

Run the full evaluation across all three architectures:

```bash
uv run python -m ragbench.evaluators.run_all \
  --dataset data/eval/romanized_nepali_rag_eval_queries_300.csv \
  --results-dir results \
  --judge-provider openai \
  --judge-model gpt-5.2 \
  --resume-detailed
```

The `--resume-detailed` flag enables checkpoint / resume support for long judge runs. This is useful because LLM-as-judge evaluation can be slow and expensive when running hundreds of queries across multiple architectures.

---

## Running Tests

```bash
uv run pytest
```

Latest verification:

```text
35 passed
```

---

## Reproducibility Notes

To make results more reliable:

- Use the same dataset for all architectures.
- Use the same internal knowledge base for all architectures.
- Use the same judge model for all judged outputs.
- Keep retrieval depth fixed when comparing architectures.
- Store per-query results, not only aggregate scores.
- Use checkpointing for long-running judge evaluations.
- Track judge errors separately.
- Keep raw generated answers for auditability.

Current run:

```text
Dataset size: 300 queries
Architectures: 3
Judged outputs: 900
Judge errors: 0
Test result: 35 passed
```

---

## Research Strengths

This project is stronger than a normal demo because it includes:

- Multiple RAG architectures
- Same benchmark dataset across all systems
- Three realistic support domains
- Romanized Nepali and code-mixed query handling
- Per-query evaluation results
- LLM-as-judge scoring
- Company-level breakdown
- Difficulty-level breakdown
- Operational metrics such as latency and success rate
- Reproducible command-line evaluation
- Checkpoint / resume support
- Automated tests

---

## Limitations

The current version is a strong research prototype, but several improvements are needed before claiming fully publishable research-grade results.

Current limitations:

- The dataset is simulated and should later be validated with real anonymized support queries.
- The internal company documents are simulated policy documents, not production company data.
- LLM-as-judge evaluation can contain judge bias.
- The overall score gap between systems is very small.
- Human evaluation has not yet been added.
- Statistical significance testing has not yet been added.
- Cost and token usage analysis should be included in future runs.

---

## Recommended Next Steps

To make the project more research-grade, add:

1. **Bootstrap confidence intervals** for all major metrics.
2. **Paired significance testing** between architectures.
3. **Human evaluation** on a stratified sample of queries.
4. **Error analysis** by company, difficulty, and support category.
5. **Cost analysis** using token usage and judge-call cost.
6. **Ablation studies** for retrieval method, chunk size, top-k, reranker, and graph retrieval.
7. **Additional baselines**, such as BM25, hybrid retrieval, reranked RAG, and query-rewrite RAG.
8. **Manual golden answers** for a subset of the benchmark.

---

## Example Queries

```text
mero order cancel garepachi refund kati din ma aaucha?
wrong item aayo bhane return kasari garne?
product available cha ki chaina kasari tha paune?
mero server down cha, SLA claim garna milcha?
ssl certificate expire bhayo bhane ke garne?
mero payment deduct bhayo tara receiver le paisa paayena
kyc verify garna kati time lagcha?
wallet limit badhauna k garnu parcha?
```

---

## Project Status

Current status:

```text
Dataset prepared: Complete
Knowledge base prepared: Complete
Traditional RAG: Complete
Agentic RAG: Complete
Agentic GraphRAG: Complete
LLM-as-judge evaluation: Complete
Detailed metrics: Complete
Summary reports: Complete
Tests: Passing
```

Latest overall result:

```text
agentic_graph_rag   0.7899
agentic_rag         0.7894
traditional_rag     0.7886
```

---

## Disclaimer

This repository is intended for research and educational purposes. The company knowledge bases are simulated and should not be treated as official policies of any real company unless explicitly replaced with verified production documents.
