# Research-Grade Evaluation of Three RAG Architectures for Romanized Nepali Customer Support

## Abstract

The highest mean overall score is achieved by `agentic_graph_rag` (mean=0.7899). Pairwise testing indicates that the main graph-vs-traditional comparison is not statistically significant. The interpretation emphasizes effect size and latency trade-offs rather than ranking by small mean differences alone.

## Experimental Setup

This analysis uses the existing `rag_metrics_detailed.jsonl` files as the source of truth. No RAG systems and no LLM judge calls are rerun by this analysis stage.

## Dataset Description

- 300 Romanized Nepali and code-mixed Nepali-English support queries.
- 3 synthetic company domains with 100 queries each.
- Difficulty labels include simple, medium, and complex.
- Query category/intent labels are used for stratified analysis.

## Architectures Compared

- `traditional_rag`
- `agentic_rag`
- `agentic_graph_rag`

## Evaluation Metrics

The analysis normalizes available metrics from the detailed JSONL files, including retrieval metrics, judged generation metrics, Romanized Nepali robustness metrics, operational latency, and computed per-query `overall_score`.

## LLM-as-Judge Configuration

Detailed metric files report judge model(s): gpt-5.2.

## Statistical Testing Methodology

Because each architecture is evaluated on the same 300 query IDs, pairwise comparisons use paired tests. The report includes paired bootstrap confidence intervals, paired permutation tests, optional Wilcoxon signed-rank p-values when SciPy is available, Cohen's dz, Cliff's delta, and Holm-Bonferroni adjusted p-values.

## Overall Results

| architecture | n | mean | median | std | ci95_low | ci95_high |
| --- | --- | --- | --- | --- | --- | --- |
| agentic_graph_rag | 300 | 0.7899 | 0.8186 | 0.1096 | 0.7774 | 0.8025 |
| agentic_rag | 300 | 0.7894 | 0.8158 | 0.1095 | 0.7769 | 0.8019 |
| traditional_rag | 300 | 0.7886 | 0.8157 | 0.1103 | 0.7759 | 0.8014 |

## Per-Company Results

| company | architecture | n | mean_overall_score | ci95_low | ci95_high | mean_latency_ms | best_architecture_for_group |
| --- | --- | --- | --- | --- | --- | --- | --- |
| Hosting / Cloud Provider | agentic_graph_rag | 100 | 0.7837 | 0.7612 | 0.8051 | 4133.9300 | agentic_rag |
| Hosting / Cloud Provider | agentic_rag | 100 | 0.7839 | 0.7620 | 0.8050 | 2721.5000 | agentic_rag |
| Hosting / Cloud Provider | traditional_rag | 100 | 0.7836 | 0.7616 | 0.8046 | 2713.2300 | agentic_rag |
| PaySathi Wallet / FinTech Payment Company | agentic_graph_rag | 100 | 0.7528 | 0.7317 | 0.7737 | 2898.4400 | agentic_graph_rag |
| PaySathi Wallet / FinTech Payment Company | agentic_rag | 100 | 0.7506 | 0.7292 | 0.7717 | 2603.1100 | agentic_graph_rag |
| PaySathi Wallet / FinTech Payment Company | traditional_rag | 100 | 0.7487 | 0.7272 | 0.7700 | 2633.3300 | agentic_graph_rag |
| QuickCommerce / E-commerce Company | agentic_graph_rag | 100 | 0.8332 | 0.8152 | 0.8508 | 2265.7500 | agentic_rag |
| QuickCommerce / E-commerce Company | agentic_rag | 100 | 0.8337 | 0.8158 | 0.8512 | 2587.6300 | agentic_rag |
| QuickCommerce / E-commerce Company | traditional_rag | 100 | 0.8337 | 0.8157 | 0.8514 | 2226.0100 | agentic_rag |

## Per-Difficulty Results

| difficulty | architecture | n | mean_overall_score | ci95_low | ci95_high | mean_latency_ms | best_architecture_for_group |
| --- | --- | --- | --- | --- | --- | --- | --- |
| complex | agentic_graph_rag | 90 | 0.7409 | 0.7189 | 0.7625 | 2619.2333 | traditional_rag |
| complex | agentic_rag | 90 | 0.7405 | 0.7193 | 0.7617 | 2705.8333 | traditional_rag |
| complex | traditional_rag | 90 | 0.7411 | 0.7195 | 0.7624 | 2649.7222 | traditional_rag |
| medium | agentic_graph_rag | 90 | 0.8058 | 0.7855 | 0.8257 | 4474.4111 | agentic_graph_rag |
| medium | agentic_rag | 90 | 0.8032 | 0.7826 | 0.8236 | 2395.2667 | agentic_graph_rag |
| medium | traditional_rag | 90 | 0.8010 | 0.7797 | 0.8216 | 2426.6111 | agentic_graph_rag |
| simple | agentic_graph_rag | 120 | 0.8147 | 0.7952 | 0.8339 | 2428.2000 | agentic_rag |
| simple | agentic_rag | 120 | 0.8157 | 0.7964 | 0.8348 | 2767.7083 | agentic_rag |
| simple | traditional_rag | 120 | 0.8150 | 0.7953 | 0.8344 | 2503.2250 | agentic_rag |

## Retrieval Quality Analysis

| architecture | mean_context_precision | mean_context_recall | hit_rate_at_k | mrr_at_k | ndcg_at_k | average_retrieved_chunks | missing_context_rate | cross_company_contamination_rate | retrieval_answer_correlation |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| agentic_graph_rag | 0.5158 | 0.7400 | 0.7400 | 0.6178 | 0.6436 | 4.0000 | 0.0000 | 0.0000 | 0.8266 |
| agentic_rag | 0.5158 | 0.7400 | 0.7400 | 0.6178 | 0.6436 | 4.0000 | 0.0000 | 0.0000 | 0.8289 |
| traditional_rag | 0.5158 | 0.7400 | 0.7400 | 0.6178 | 0.6436 | 4.0000 | 0.0000 | 0.0000 | 0.8341 |

Retrieval scores are effectively tied across architectures when they use the same underlying retrieval output pattern. Any claimed advantage should therefore come from downstream reasoning/generation metrics, not retrieval alone.

## Latency and Efficiency Analysis

| architecture | mean_quality_score | mean_latency_ms | p95_latency_ms | quality_gain_over_traditional_rag | latency_overhead_ms_over_traditional_rag | quality_gain_per_extra_second |
| --- | --- | --- | --- | --- | --- | --- |
| agentic_graph_rag | 0.7899 | 3099.3733 | 3569.7000 | 0.0012 | 575.1833 | 0.0021 |
| agentic_rag | 0.7894 | 2637.4133 | 3548.1500 | 0.0007 | 113.2233 | 0.0065 |
| traditional_rag | 0.7886 | 2524.1900 | 3509.7500 | 0.0000 | 0.0000 |  |

## Failure Analysis

| architecture | failure_type | count | rate |
| --- | --- | --- | --- |
| agentic_graph_rag | retrieval miss | 12 | 0.0400 |
| agentic_graph_rag | irrelevant retrieval | 5 | 0.0167 |
| agentic_graph_rag | partial answer | 12 | 0.0400 |
| agentic_graph_rag | hallucinated policy | 12 | 0.0400 |
| agentic_graph_rag | wrong company policy | 0 | 0.0000 |
| agentic_graph_rag | wrong action recommendation | 1 | 0.0033 |
| agentic_graph_rag | poor handling of complex Romanized Nepali | 1 | 0.0033 |
| agentic_graph_rag | ambiguity not clarified | 2 | 0.0067 |
| agentic_graph_rag | over-answering | 0 | 0.0000 |
| agentic_graph_rag | under-answering | 0 | 0.0000 |
| agentic_graph_rag | latency overhead without quality gain | 5 | 0.0167 |
| agentic_rag | retrieval miss | 14 | 0.0467 |
| agentic_rag | irrelevant retrieval | 9 | 0.0300 |
| agentic_rag | partial answer | 14 | 0.0467 |
| agentic_rag | hallucinated policy | 13 | 0.0433 |
| agentic_rag | wrong company policy | 0 | 0.0000 |
| agentic_rag | wrong action recommendation | 0 | 0.0000 |
| agentic_rag | poor handling of complex Romanized Nepali | 2 | 0.0067 |
| agentic_rag | ambiguity not clarified | 4 | 0.0133 |
| agentic_rag | over-answering | 0 | 0.0000 |
| agentic_rag | under-answering | 0 | 0.0000 |
| agentic_rag | latency overhead without quality gain | 1 | 0.0033 |
| traditional_rag | retrieval miss | 17 | 0.0567 |
| traditional_rag | irrelevant retrieval | 7 | 0.0233 |
| traditional_rag | partial answer | 17 | 0.0567 |
| traditional_rag | hallucinated policy | 14 | 0.0467 |
| traditional_rag | wrong company policy | 0 | 0.0000 |
| traditional_rag | wrong action recommendation | 1 | 0.0033 |
| traditional_rag | poor handling of complex Romanized Nepali | 2 | 0.0067 |
| traditional_rag | ambiguity not clarified | 6 | 0.0200 |
| traditional_rag | over-answering | 0 | 0.0000 |
| traditional_rag | under-answering | 0 | 0.0000 |
| traditional_rag | latency overhead without quality gain | 0 | 0.0000 |

## Statistical Significance Results

| comparison | mean_difference_a_minus_b | bootstrap_ci_low | bootstrap_ci_high | permutation_p_value | holm_adjusted_p_value | wilcoxon_p_value | cohens_dz | cliffs_delta | conclusion |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| traditional_rag_vs_agentic_rag | -0.0007 | -0.0031 | 0.0016 | 0.5332 | 1.0000 | 0.5475 | -0.0366 | -0.0167 | not statistically significant |
| traditional_rag_vs_agentic_graph_rag | -0.0012 | -0.0036 | 0.0012 | 0.3212 | 0.9635 | 0.4752 | -0.0580 | -0.0700 | not statistically significant |
| agentic_rag_vs_agentic_graph_rag | -0.0005 | -0.0028 | 0.0019 | 0.6837 | 1.0000 | 0.7939 | -0.0238 | 0.0433 | not statistically significant |

## Practical Interpretation

Best mean quality: `agentic_graph_rag`. Fastest mean latency: `traditional_rag`. Best quality-latency trade-off: `traditional_rag`. `agentic_graph_rag` vs `traditional_rag`: not statistically significant with mean difference 0.0012. `agentic_graph_rag` vs `agentic_rag`: not statistically significant with mean difference 0.0005.

## Threats to Validity

- The benchmark uses synthetic companies and synthetic queries, so external validity depends on future real-world data.
- LLM-as-judge scores can encode model-specific preferences.
- The current architectures appear to share much of the retrieval surface, reducing the chance of observing large retrieval differences.
- Per-query overall score is a normalized composite; different metric weighting could change the final ordering.

## Limitations

- Token usage, agent steps, and tool-call counts are unavailable in the current detailed result files.
- Gold answer points and expected source documents are sparse or absent, so judge metrics carry more weight for generation quality.
- Statistical significance does not imply product relevance when effect sizes are tiny.

## Final Conclusion

- Highest mean score: `agentic_graph_rag`.
- Is `agentic_graph_rag` significantly better than `traditional_rag`? No (not statistically significant).
- Is the advantage practically meaningful? No.
- Fastest architecture: `traditional_rag`.
- Best for simple queries: `agentic_rag`.
- Best for complex queries: `traditional_rag`.
- Most production-ready: `traditional_rag` based on current quality-latency evidence.
- Final research claim: report the systems as closely matched unless the adjusted paired tests show a clear and practically meaningful effect.

## Recommendations for Next Experiment

- Add human-authored gold answer points and expected source documents for every query.
- Add true agent-step and tool-call telemetry for agentic systems.
- Evaluate on a larger and more realistic query set with adversarial Romanized Nepali spelling variants.
- Run cost-aware evaluation that includes input/output tokens and infrastructure overhead.
- Include human evaluation for a stratified sample to calibrate LLM-as-judge scores.

## Validation Summary

- Overall validation status: `True`
- Query alignment valid: `True`
- Field alignment valid: `True`