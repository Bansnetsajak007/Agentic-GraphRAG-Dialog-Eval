# RAG Evaluation Report

## Objective

Evaluate Traditional RAG, Agentic RAG, and Agentic GraphRAG for a Romanized Nepali customer-support benchmark using retrieval, generation, language robustness, and operational metrics.

## Dataset Description

- Dataset path: `data/eval/romanized_nepali_rag_eval_queries_300.csv`
- 300 Romanized Nepali/code-mixed customer-support queries.
- 3 company domains: quick-commerce/e-commerce, hosting/cloud provider, and FinTech/digital wallet.
- 100 queries per company with simple, medium, and complex/adversarial difficulty levels.
- Current dataset provides expected topic/category metadata. Gold answer points and expected source docs are used automatically when present.

## Architectures Compared

- `traditional_rag`
- `agentic_rag`
- `agentic_graph_rag`

## Metrics Used

- Retrieval: context precision, context recall, context relevancy, hit rate@k, MRR@k, nDCG@k, retrieved chunk count.
- Generation: faithfulness/groundedness, answer relevancy, correctness, completeness, hallucination rate, policy compliance.
- Romanized Nepali support: query understanding, code-mixed handling, intent classification accuracy, company-domain accuracy, escalation correctness, tone appropriateness.
- Operational: success/failure rate, average/p50/p95 latency, token usage, agent steps, tool calls when available.

Judge status: LLM judge enabled with `openai` model `gpt-5.2`.

## Overall Comparison Table

| architecture | total_queries | success_rate | overall_score | retrieval_quality_score | generation_quality_score | romanized_robustness_score | average_latency_ms | p95_latency_ms |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| agentic_graph_rag | 300 | 1.0000 | 0.7899 | 0.5510 | 0.6974 | 0.9112 | 3099.3733 | 3569.7000 |
| agentic_rag | 300 | 1.0000 | 0.7894 | 0.5510 | 0.6944 | 0.9122 | 2637.4133 | 3548.1500 |
| traditional_rag | 300 | 1.0000 | 0.7886 | 0.5510 | 0.6927 | 0.9109 | 2524.1900 | 3509.7500 |

## Company-Wise Comparison

| architecture | company | success_rate | overall_score | context_recall | hit_rate_at_k | answer_relevancy | average_latency_ms |
| --- | --- | --- | --- | --- | --- | --- | --- |
| agentic_graph_rag | Hosting / Cloud Provider | 1.0000 | 0.7837 | 0.7700 | 0.7700 | 0.7319 | 4133.9300 |
| agentic_graph_rag | PaySathi Wallet / FinTech Payment Company | 1.0000 | 0.7528 | 0.5200 | 0.5200 | 0.8119 | 2898.4400 |
| agentic_graph_rag | QuickCommerce / E-commerce Company | 1.0000 | 0.8332 | 0.9300 | 0.9300 | 0.7301 | 2265.7500 |
| agentic_rag | Hosting / Cloud Provider | 1.0000 | 0.7839 | 0.7700 | 0.7700 | 0.7234 | 2721.5000 |
| agentic_rag | PaySathi Wallet / FinTech Payment Company | 1.0000 | 0.7506 | 0.5200 | 0.5200 | 0.8023 | 2603.1100 |
| agentic_rag | QuickCommerce / E-commerce Company | 1.0000 | 0.8337 | 0.9300 | 0.9300 | 0.7350 | 2587.6300 |
| traditional_rag | Hosting / Cloud Provider | 1.0000 | 0.7836 | 0.7700 | 0.7700 | 0.7386 | 2713.2300 |
| traditional_rag | PaySathi Wallet / FinTech Payment Company | 1.0000 | 0.7487 | 0.5200 | 0.5200 | 0.8093 | 2633.3300 |
| traditional_rag | QuickCommerce / E-commerce Company | 1.0000 | 0.8337 | 0.9300 | 0.9300 | 0.7257 | 2226.0100 |

## Difficulty-Wise Comparison

| architecture | difficulty | success_rate | overall_score | context_recall | answer_relevancy | escalation_correctness | average_latency_ms |
| --- | --- | --- | --- | --- | --- | --- | --- |
| agentic_graph_rag | complex | 1.0000 | 0.7409 | 0.5667 | 0.7599 | 0.7833 | 2619.2333 |
| agentic_graph_rag | medium | 1.0000 | 0.8058 | 0.8222 | 0.7641 | 0.6944 | 4474.4111 |
| agentic_graph_rag | simple | 1.0000 | 0.8147 | 0.8083 | 0.7519 | 0.7667 | 2428.2000 |
| agentic_rag | complex | 1.0000 | 0.7405 | 0.5667 | 0.7452 | 0.7778 | 2705.8333 |
| agentic_rag | medium | 1.0000 | 0.8032 | 0.8222 | 0.7680 | 0.7056 | 2395.2667 |
| agentic_rag | simple | 1.0000 | 0.8157 | 0.8083 | 0.7490 | 0.7708 | 2767.7083 |
| traditional_rag | complex | 1.0000 | 0.7411 | 0.5667 | 0.7552 | 0.7833 | 2649.7222 |
| traditional_rag | medium | 1.0000 | 0.8010 | 0.8222 | 0.7753 | 0.6778 | 2426.6111 |
| traditional_rag | simple | 1.0000 | 0.8150 | 0.8083 | 0.7468 | 0.7708 | 2503.2250 |

## Latency and Efficiency Comparison

| architecture | average_latency_ms | p50_latency_ms | p95_latency_ms | average_token_usage | average_agent_steps | average_tool_calls |
| --- | --- | --- | --- | --- | --- | --- |
| agentic_graph_rag | 3099.3733 | 2354.5000 | 3569.7000 |  |  |  |
| agentic_rag | 2637.4133 | 2351.0000 | 3548.1500 |  |  |  |
| traditional_rag | 2524.1900 | 2353.0000 | 3509.7500 |  |  |  |

## Retrieval-Quality Comparison

| architecture | context_precision | context_recall | context_relevancy | hit_rate_at_k | mrr_at_k | ndcg_at_k | average_retrieved_chunks |
| --- | --- | --- | --- | --- | --- | --- | --- |
| agentic_graph_rag | 0.5158 | 0.7400 | 0.0488 | 0.7400 | 0.6178 | 0.6436 | 4.0000 |
| agentic_rag | 0.5158 | 0.7400 | 0.0488 | 0.7400 | 0.6178 | 0.6436 | 4.0000 |
| traditional_rag | 0.5158 | 0.7400 | 0.0488 | 0.7400 | 0.6178 | 0.6436 | 4.0000 |

## Generation-Quality Comparison

| architecture | faithfulness | answer_relevancy | answer_correctness | answer_completeness | hallucination_rate | policy_compliance |
| --- | --- | --- | --- | --- | --- | --- |
| agentic_graph_rag | 0.7245 | 0.7580 | 0.6649 | 0.4918 | 0.2755 | 0.8206 |
| agentic_rag | 0.7226 | 0.7536 | 0.6584 | 0.4937 | 0.2774 | 0.8152 |
| traditional_rag | 0.7180 | 0.7579 | 0.6574 | 0.4862 | 0.2820 | 0.8184 |

## Romanized Nepali Robustness Comparison

| architecture | romanized_query_understanding | code_mixed_handling | intent_classification_accuracy | company_domain_accuracy | escalation_correctness | tone_appropriateness |
| --- | --- | --- | --- | --- | --- | --- |
| agentic_graph_rag | 0.8339 | 1.0000 | 1.0000 | 1.0000 | 0.7500 | 0.8832 |
| agentic_rag | 0.8347 | 1.0000 | 1.0000 | 1.0000 | 0.7533 | 0.8851 |
| traditional_rag | 0.8349 | 1.0000 | 1.0000 | 1.0000 | 0.7467 | 0.8841 |

## Error Analysis

- Total evaluated records: 900
- Failed records: 0
- Records with no retrieved chunks: 0
- Records below hit-rate threshold: 234
- Records below faithfulness threshold: 187
- Records below answer-relevancy threshold: 110
- Records below tone-appropriateness threshold: 2

## Final Conclusion

`agentic_graph_rag` has the highest computed overall score in this run. The conclusion is based on the available deterministic metrics and any configured judge metrics. If judge metrics were disabled, treat generation-quality conclusions as provisional and rerun with `JUDGE_LLM_PROVIDER` configured for stronger answer-quality assessment.
