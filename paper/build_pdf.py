"""Render the polished WOCHAT-style paper PDF.

The canonical source is ``paper/wochat2026_rag_eval.tex``.  This environment
does not provide a TeX engine, so the local PDF artifact is generated with
ReportLab using the same manuscript content and a compact two-column layout.
"""

from __future__ import annotations

from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.platypus import (
    BaseDocTemplate,
    Frame,
    Image,
    PageTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
)


ROOT = Path(__file__).resolve().parents[1]
PAPER_DIR = ROOT / "paper"
FIG_DIR = ROOT / "results/analysis/figures"
OUTPUT_PATH = PAPER_DIR / "wochat2026_rag_eval.pdf"


def main() -> None:
    doc = build_document()
    styles = build_styles()
    story: list = []
    add_title_block(story, styles)
    add_body(story, styles)
    doc.build(story)
    print(f"Wrote {OUTPUT_PATH}")


def build_document() -> BaseDocTemplate:
    margin_x = 0.52 * inch
    bottom = 0.52 * inch
    top = 0.48 * inch
    gap = 0.20 * inch
    column_width = (letter[0] - 2 * margin_x - gap) / 2

    first_title_h = 1.92 * inch
    body_h_first = letter[1] - top - bottom - first_title_h
    title_frame = Frame(
        margin_x,
        letter[1] - top - first_title_h,
        letter[0] - 2 * margin_x,
        first_title_h,
        leftPadding=0,
        rightPadding=0,
        topPadding=0,
        bottomPadding=0,
    )
    first_left = Frame(
        margin_x,
        bottom,
        column_width,
        body_h_first,
        leftPadding=0,
        rightPadding=0,
        topPadding=0,
        bottomPadding=0,
    )
    first_right = Frame(
        margin_x + column_width + gap,
        bottom,
        column_width,
        body_h_first,
        leftPadding=0,
        rightPadding=0,
        topPadding=0,
        bottomPadding=0,
    )
    body_h = letter[1] - top - bottom
    body_left = Frame(
        margin_x,
        bottom,
        column_width,
        body_h,
        leftPadding=0,
        rightPadding=0,
        topPadding=0,
        bottomPadding=0,
    )
    body_right = Frame(
        margin_x + column_width + gap,
        bottom,
        column_width,
        body_h,
        leftPadding=0,
        rightPadding=0,
        topPadding=0,
        bottomPadding=0,
    )
    doc = BaseDocTemplate(
        str(OUTPUT_PATH),
        pagesize=letter,
        title="Are Agentic and Graph-Augmented RAG Worth It for Romanized Nepali Customer Support?",
        author="Sajak Basnet",
        leftMargin=margin_x,
        rightMargin=margin_x,
        topMargin=top,
        bottomMargin=bottom,
    )
    doc.addPageTemplates(
        [
            PageTemplate(
                id="First",
                frames=[title_frame, first_left, first_right],
                onPage=footer,
                autoNextPageTemplate="Body",
            ),
            PageTemplate(id="Body", frames=[body_left, body_right], onPage=footer),
        ]
    )
    return doc


def build_styles() -> dict[str, ParagraphStyle]:
    base = getSampleStyleSheet()
    return {
        "title": ParagraphStyle(
            "PaperTitle",
            parent=base["Title"],
            fontName="Times-Bold",
            fontSize=16.6,
            leading=18.4,
            alignment=TA_CENTER,
            spaceAfter=3,
        ),
        "subtitle": ParagraphStyle(
            "Subtitle",
            parent=base["Normal"],
            fontName="Times-Roman",
            fontSize=11.2,
            leading=12.6,
            alignment=TA_CENTER,
            spaceAfter=5,
        ),
        "author": ParagraphStyle(
            "Author",
            parent=base["Normal"],
            fontName="Times-Roman",
            fontSize=9.4,
            leading=10.5,
            alignment=TA_CENTER,
            spaceAfter=4,
        ),
        "abstract_heading": ParagraphStyle(
            "AbstractHeading",
            parent=base["Normal"],
            fontName="Times-Bold",
            fontSize=8.9,
            leading=9.8,
            alignment=TA_CENTER,
            spaceBefore=2,
            spaceAfter=1,
        ),
        "abstract": ParagraphStyle(
            "Abstract",
            parent=base["BodyText"],
            fontName="Times-Roman",
            fontSize=8.25,
            leading=9.25,
            alignment=TA_JUSTIFY,
            leftIndent=0.35 * inch,
            rightIndent=0.35 * inch,
            spaceAfter=0,
        ),
        "h1": ParagraphStyle(
            "Heading1",
            parent=base["Heading1"],
            fontName="Times-Bold",
            fontSize=10.9,
            leading=12.1,
            spaceBefore=6,
            spaceAfter=2,
        ),
        "body": ParagraphStyle(
            "Body",
            parent=base["BodyText"],
            fontName="Times-Roman",
            fontSize=8.95,
            leading=10.05,
            alignment=TA_JUSTIFY,
            spaceAfter=2.5,
        ),
        "caption": ParagraphStyle(
            "Caption",
            parent=base["BodyText"],
            fontName="Times-Italic",
            fontSize=7.15,
            leading=7.8,
            alignment=TA_CENTER,
            spaceBefore=1,
            spaceAfter=3,
        ),
        "quote": ParagraphStyle(
            "Quote",
            parent=base["BodyText"],
            fontName="Times-Italic",
            fontSize=8.2,
            leading=9.0,
            alignment=TA_CENTER,
            leftIndent=0.08 * inch,
            rightIndent=0.08 * inch,
            spaceAfter=3,
        ),
    }


def add_title_block(story: list, styles: dict[str, ParagraphStyle]) -> None:
    story.append(
        Paragraph(
            "Are Agentic and Graph-Augmented RAG Worth It for Romanized Nepali Customer Support?",
            styles["title"],
        )
    )
    story.append(
        Paragraph(
            "A Controlled Evaluation across Three Synthetic Service Domains",
            styles["subtitle"],
        )
    )
    story.append(
        Paragraph(
            "Sajak Basnet<br/>Gomendra College<br/>"
            "<font name='Courier'>sajak55460@gomendracollege.edu.np</font>",
            styles["author"],
        )
    )
    story.append(Paragraph("Abstract", styles["abstract_heading"]))
    story.append(
        Paragraph(
            "Retrieval-augmented generation (RAG) is attractive for customer-support dialogue because answers must be both conversational and grounded in policy. For low-resource, code-mixed settings such as Romanized Nepali, however, it is unclear whether complex agentic and graph-augmented RAG systems provide reliable gains over a controlled semantic baseline. We evaluate traditional RAG, agentic RAG, and agentic GraphRAG on 300 matched Romanized Nepali support queries across quick-commerce, cloud hosting, and digital wallet domains. The evaluation combines deterministic retrieval and operational metrics, GPT-5.2 LLM-as-judge scoring, stratified error analysis, paired bootstrap confidence intervals, paired permutation tests, Wilcoxon tests, and Holm-Bonferroni correction. Agentic GraphRAG obtains the highest mean score (0.7899), but the graph-over-traditional gain is only 0.0012, is not statistically significant, and is not practically meaningful. Traditional RAG is fastest and has the best quality-latency trade-off.",
            styles["abstract"],
        )
    )


def add_body(story: list, styles: dict[str, ParagraphStyle]) -> None:
    section(
        story,
        styles,
        "1 Introduction",
        [
            "Customer-support dialogue is a practical testbed for retrieval-augmented generation. A support assistant must answer in a helpful tone, respect company policy, decline unsupported actions, and expose the right escalation path. These requirements become sharper in Romanized Nepali, where customers write informal transliterations, use flexible spellings, mix English service terms, and omit context. A query such as <i>mero order kata pugyo ani cancel garna milcha?</i> is short, code-mixed, intent-rich, and company-specific.",
            "Recent RAG systems increasingly add query rewriting, routing, planning, tool use, memory, verification, and graph lookup. Such mechanisms are appealing because support problems contain hidden structure: accounts, orders, refunds, invoices, incidents, and escalation rules. Yet each mechanism also increases latency, implementation cost, evaluation complexity, and failure surface. For an industry support system, a method should not be preferred merely because its mean score is slightly higher.",
        ],
    )
    story.append(
        Paragraph(
            "Research question: Do agentic RAG and agentic GraphRAG provide measurable advantages over traditional semantic RAG for Romanized Nepali customer support?",
            styles["quote"],
        )
    )
    section(
        story,
        styles,
        "2 Benchmark and Systems",
        [
            "The dataset contains 300 Romanized Nepali and code-mixed Nepali-English support queries, with 100 queries per company. The companies are a quick-commerce/e-commerce provider, a hosting/cloud provider, and a FinTech/digital wallet provider. Each query includes a query identifier, company label, difficulty label, category or intent, and user query text.",
            "Each company has an internal Markdown knowledge base covering policy, support tone, operational procedures, incident handling, and escalation rules. Documents are chunked deterministically and indexed in company-specific vector collections. During evaluation, the query's company label selects the corresponding knowledge base, which prevents accidental cross-domain comparison while still allowing detection of cross-company contamination.",
            "Traditional RAG embeds the query, retrieves top-k chunks, and generates an answer from retrieved context. Agentic RAG and agentic GraphRAG are evaluated from their existing saved output streams as separate architecture conditions. No RAG system or LLM judge is rerun during this paper-level analysis.",
        ],
    )
    section(
        story,
        styles,
        "3 Evaluation Methodology",
        [
            "The evaluator computes retrieval, generation, Romanized Nepali robustness, and operational metrics. Retrieval metrics include context precision, context recall, context relevancy, hit rate@k, MRR@k, nDCG@k, average retrieved chunks, empty retrieval rate, duplicate chunk rate, and cross-company contamination. Generation metrics include groundedness, answer relevancy, correctness, completeness, hallucination rate, and policy compliance. Robustness metrics include romanized query understanding, code-mixed handling, intent classification accuracy, company-domain accuracy, escalation correctness, and tone appropriateness.",
            "GPT-5.2 is used as the judge for faithfulness, answer relevancy, answer correctness, completeness, policy compliance, Romanized query understanding, and tone. The judge receives the query, generated answer, retrieved context, and available expected topic or source metadata. To reduce overclaiming from judge preferences, the analysis combines judge scores with deterministic retrieval checks and paired statistical tests.",
            "Because all architectures answer the same 300 query IDs, all comparisons are paired. We compute bootstrap confidence intervals over per-query means, paired bootstrap confidence intervals for architecture differences, paired permutation tests, Wilcoxon signed-rank tests when available, Cohen's dz, Cliff's delta, and Holm-Bonferroni adjusted p-values. Differences below 0.01 on the normalized overall score are treated as not practically meaningful.",
        ],
    )
    add_table(
        story,
        styles,
        "Table 1. Overall GPT-5.2 judged composite scores.",
        [
            ["Architecture", "Mean", "95% CI", "Median", "Std."],
            ["Traditional", "0.7886", "[0.7759, 0.8014]", "0.8157", "0.1103"],
            ["Agentic", "0.7894", "[0.7769, 0.8019]", "0.8158", "0.1095"],
            ["GraphRAG", "0.7899", "[0.7774, 0.8025]", "0.8186", "0.1096"],
        ],
    )
    add_table(
        story,
        styles,
        "Table 2. Paired significance tests. All corrected comparisons are non-significant.",
        [
            ["Comparison", "Diff.", "95% CI", "Holm p", "dz"],
            ["Trad-Agentic", "-0.0007", "[-0.0031, 0.0016]", "1.0000", "-0.0366"],
            ["Trad-Graph", "-0.0012", "[-0.0036, 0.0012]", "0.9635", "-0.0580"],
            ["Agentic-Graph", "-0.0005", "[-0.0028, 0.0019]", "1.0000", "-0.0238"],
        ],
    )
    section(
        story,
        styles,
        "4 Overall Results",
        [
            "Agentic GraphRAG has the highest mean score, but the absolute graph-over-traditional gain is only 0.0012. The standard deviations are nearly identical and the confidence intervals almost fully overlap. Every paired confidence interval crosses zero, every Holm-corrected p-value is non-significant at alpha=0.05, and the paired effect sizes are negligible.",
            "The correct interpretation is therefore conservative: the three systems are closely matched under this benchmark. The result is not evidence that GraphRAG is definitively better; it is evidence that the current graph and agentic variants do not yet produce a measurable advantage over a controlled semantic baseline.",
        ],
    )
    add_image(
        story,
        styles,
        FIG_DIR / "overall_score_by_architecture_ci.png",
        "Figure 1. Mean overall score by architecture with 95% bootstrap confidence intervals.",
    )
    add_image(
        story,
        styles,
        FIG_DIR / "score_distribution_boxplot_by_architecture.png",
        "Figure 2. Query-level score distributions. The central tendency and spread are closely matched.",
    )
    section(
        story,
        styles,
        "5 Stratified Analysis",
        [
            "Stratification avoids hiding domain-specific behavior. On hosting/cloud and quick-commerce, agentic RAG is marginally highest. On the wallet domain, GraphRAG is marginally highest. By difficulty, agentic RAG is marginally highest on simple queries, GraphRAG on medium queries, and traditional RAG on complex queries. None of these differences is large enough to support a strong subgroup claim.",
            "The complex-query result is especially important. If graph retrieval were paying off, the graph condition should improve most on hard multi-constraint queries. Instead, complex-query means are 0.7411 for traditional RAG, 0.7409 for GraphRAG, and 0.7405 for agentic RAG. The architecture advantage does not increase with difficulty in this run.",
        ],
    )
    add_table(
        story,
        styles,
        "Table 3. Best mean score by stratum. All wins are practical ties.",
        [
            ["Group", "Best", "Score", "Latency", "Note"],
            ["Hosting/cloud", "Agentic", "0.7839", "2722", "tied"],
            ["Wallet/FinTech", "Graph", "0.7528", "2898", "tied"],
            ["Quick-commerce", "Agentic", "0.8337", "2588", "tied"],
            ["Simple", "Agentic", "0.8157", "2768", "tied"],
            ["Medium", "Graph", "0.8058", "4474", "tied"],
            ["Complex", "Traditional", "0.7411", "2650", "tied"],
        ],
    )
    add_image(
        story,
        styles,
        FIG_DIR / "score_by_difficulty_architecture.png",
        "Figure 3. Mean score by difficulty and architecture.",
    )
    add_image(
        story,
        styles,
        FIG_DIR / "score_by_company_architecture.png",
        "Figure 4. Mean score by company and architecture.",
    )
    section(
        story,
        styles,
        "6 Retrieval, Latency, and Efficiency",
        [
            "Retrieval behavior explains much of the outcome. All three systems retrieve four chunks on average and have identical context recall (0.7400), hit rate@k (0.7400), and MRR@k (0.6178). The analysis detects no empty retrieval and no cross-company contamination. Retrieval quality correlates strongly with final answer score, about 0.83 for all systems.",
            "Traditional RAG is fastest, with mean latency 2524 ms and p95 latency 3510 ms. Agentic RAG adds 113 ms for a 0.0007 quality gain. GraphRAG adds 575 ms for a 0.0012 quality gain. These ratios do not justify a production switch under the current evidence.",
        ],
    )
    add_table(
        story,
        styles,
        "Table 4. Quality-latency trade-off relative to traditional RAG.",
        [
            ["Architecture", "Mean ms", "p95 ms", "Gain", "Gain/sec"],
            ["Traditional", "2524", "3510", "--", "--"],
            ["Agentic", "2637", "3548", "0.0007", "0.0065"],
            ["GraphRAG", "3099", "3570", "0.0012", "0.0021"],
        ],
    )
    add_image(
        story,
        styles,
        FIG_DIR / "quality_vs_latency_scatter.png",
        "Figure 5. Quality-latency scatter. The highest mean quality also carries the largest latency overhead.",
    )
    add_image(
        story,
        styles,
        FIG_DIR / "latency_distribution_by_architecture.png",
        "Figure 6. Latency distributions by architecture.",
    )
    add_image(
        story,
        styles,
        FIG_DIR / "pairwise_score_difference_plot.png",
        "Figure 7. Paired score differences. Intervals crossing zero prevent a superiority claim.",
    )
    add_image(
        story,
        styles,
        FIG_DIR / "metric_radar_chart.png",
        "Figure 8. Metric radar summary across evaluated dimensions.",
    )
    section(
        story,
        styles,
        "7 Failure Analysis",
        [
            "Failure counts are low overall, but the taxonomy clarifies where future work should focus. Traditional RAG has 17 retrieval-miss flags, 17 partial-answer flags, and 14 hallucinated-policy flags. Agentic RAG has 14, 14, and 13 respectively. GraphRAG has 12, 12, and 12 respectively, but also 5 cases labeled as latency overhead without quality gain. No architecture shows wrong-company policy contamination.",
            "Representative low-scoring examples show that failures are rarely caused by Nepali surface form alone. More often, the answer misses a policy condition, gives a partially correct escalation path, or answers confidently when the retrieved context is incomplete. This suggests that the next useful improvement is denser gold supervision for expected source documents, expected answer points, and ambiguity handling.",
        ],
    )
    add_image(
        story,
        styles,
        FIG_DIR / "failure_type_count_by_architecture.png",
        "Figure 9. Failure-type counts by architecture.",
    )
    section(
        story,
        styles,
        "8 Practical Interpretation",
        [
            "For an industry deployment, the fastest statistically tied model is usually the better default. Traditional RAG has the simplest operational path: fewer moving parts, lower mean latency, lower tail latency, and no observed quality disadvantage after paired testing. Agentic RAG is still useful as an experimentation layer when future runs add real planning, clarification, or verifier behavior. GraphRAG is most promising as a research direction if it can change evidence selection, reduce retrieval misses, or improve complex-query handling rather than only adding orchestration overhead.",
            "For a research claim, the strongest result is negative but valuable: under controlled retrieval, the additional architecture labels do not automatically create measurable gains in Romanized Nepali customer support. This is publishable because it discourages architecture inflation and emphasizes statistical testing, matched-query evaluation, and latency-aware interpretation.",
        ],
    )
    section(
        story,
        styles,
        "9 Threats to Validity",
        [
            "The benchmark uses synthetic companies and synthetic queries, so real traffic may expose different ambiguity, spelling, and adversarial patterns. GPT-5.2 judge scores may reflect judge-model preferences despite deterministic checks. Gold answer points and expected source documents are incomplete for some queries, increasing reliance on judge scoring. The current agentic and graph-labeled outputs share much of the retrieval surface with the baseline, limiting the opportunity for large retrieval differences.",
        ],
    )
    section(
        story,
        styles,
        "10 Conclusion",
        [
            "Agentic GraphRAG has the highest mean score, but the advantage is not statistically significant and not practically meaningful. Traditional RAG is fastest and has the best quality-latency trade-off. Simple, medium, and complex query strata all show practical ties rather than a stable architecture winner.",
            "The final research claim should be conservative and credible: on this Romanized Nepali customer-support benchmark, traditional RAG, agentic RAG, and agentic GraphRAG perform similarly; the current evidence does not justify claiming that agentic or graph-augmented RAG is superior to a controlled semantic baseline. The next experiment should add human-authored gold answer points, expected source documents for every query, real user traffic, and telemetry for token cost, tool calls, graph hops, and agent steps.",
        ],
    )
    section(
        story,
        styles,
        "11 Recommendations for the Next Experiment",
        [
            "The next benchmark version should separate mechanism from label. A true agentic condition should log planning steps, clarification decisions, tool calls, verifier decisions, and fallback behavior. A true graph condition should log entity linking, graph hops, relation types, and whether graph-selected evidence differs from vector-selected evidence. Without this telemetry, it is difficult to explain why a method wins or loses.",
            "The dataset should also add complete expected answer points and expected source documents for every query. This would allow stronger deterministic scoring of source coverage, contradiction, and missing policy conditions. A small human review set should calibrate the LLM judge, especially for Romanized Nepali tone, ambiguity handling, and code-mixed intent. Finally, the production comparison should include cost per query, p99 latency, rate-limit behavior, and human handoff accuracy.",
        ],
    )
    section(
        story,
        styles,
        "12 Ethics, Scope, and Artifact Availability",
        [
            "The benchmark is synthetic and does not contain private customer messages, account identifiers, payment credentials, or real support transcripts. This lowers privacy risk but also limits ecological validity. Any future deployment study should obtain consent or use properly anonymized support data, include human review for sensitive financial and hosting decisions, and make escalation behavior explicit.",
            "The benchmark should not be interpreted as a production chatbot release. It is an evaluation artifact for studying retrieval, grounding, code-mixed language handling, and architecture trade-offs. The safest current deployment interpretation is to use traditional RAG as a strong baseline, log failures, and reserve agentic or graph mechanisms for controlled experiments where their added retrieval decisions are observable.",
            "All generated analysis files, detailed metric JSONL outputs, figures, and the paper-generation script are stored in the repository. This makes the reported tables auditable: a reviewer can inspect the exact per-query scores, validation summary, significance tests, failure taxonomy, and chart data rather than relying only on aggregate claims.",
        ],
    )
    section(
        story,
        styles,
        "13 Reviewer-Facing Takeaway",
        [
            "The central contribution is a disciplined negative result. In low-resource RAG work, it is tempting to report the highest mean architecture as the winner. This paper instead shows that matched-query evaluation, confidence intervals, multiple-comparison correction, and latency accounting can change the conclusion. The paper is therefore useful even though the final recommendation is conservative.",
            "For WOCHAT, the relevance is the intersection of agentic dialogue systems, multilingual conversational systems, robust and trustworthy evaluation, and human-AI support interaction. The benchmark focuses on Romanized Nepali because this is a common real user behavior that is poorly represented by standard English-only support benchmarks.",
        ],
    )
    section(
        story,
        styles,
        "Reproducibility",
        [
            "All result files are stored under results/. The research analysis can be regenerated with: uv run python -m ragbench.analysis.research_grade_eval --results-dir results --output-dir results/analysis --bootstrap-samples 10000 --alpha 0.05",
        ],
    )
    section(
        story,
        styles,
        "References",
        [
            "Lewis et al. (2020), Retrieval-Augmented Generation for Knowledge-Intensive NLP Tasks. Gao et al. (2023), Retrieval-Augmented Generation for Large Language Models: A Survey. Liu et al. (2023), G-Eval. Kocmi and Federmann (2023), LLMs as evaluators. Guo et al. (2023), aligning LLM judges with human preferences. Ji et al. (2023), Survey of Hallucination in Natural Language Generation. Efron and Tibshirani (1994), An Introduction to the Bootstrap. Demsar (2006), Statistical Comparisons of Classifiers over Multiple Data Sets.",
        ],
    )


def section(story: list, styles: dict[str, ParagraphStyle], heading: str, paragraphs: list[str]) -> None:
    story.append(Paragraph(heading, styles["h1"]))
    for paragraph in paragraphs:
        story.append(Paragraph(paragraph, styles["body"]))


def add_table(story: list, styles: dict[str, ParagraphStyle], caption: str, data: list[list[str]]) -> None:
    table = Table(data, repeatRows=1, hAlign="CENTER")
    table.setStyle(
        TableStyle(
            [
                ("FONT", (0, 0), (-1, 0), "Times-Bold", 7.1),
                ("FONT", (0, 1), (-1, -1), "Times-Roman", 6.9),
                ("ALIGN", (0, 0), (-1, -1), "CENTER"),
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#EEF2F7")),
                ("LINEABOVE", (0, 0), (-1, 0), 0.6, colors.black),
                ("LINEBELOW", (0, 0), (-1, 0), 0.4, colors.black),
                ("LINEBELOW", (0, -1), (-1, -1), 0.6, colors.black),
                ("LEFTPADDING", (0, 0), (-1, -1), 2.2),
                ("RIGHTPADDING", (0, 0), (-1, -1), 2.2),
                ("TOPPADDING", (0, 0), (-1, -1), 1.6),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 1.6),
            ]
        )
    )
    story.append(Spacer(1, 2))
    story.append(table)
    story.append(Paragraph(caption, styles["caption"]))


def add_image(story: list, styles: dict[str, ParagraphStyle], path: Path, caption: str) -> None:
    if not path.exists():
        return
    image = Image(str(path), width=3.60 * inch, height=2.42 * inch)
    image.hAlign = "CENTER"
    story.append(Spacer(1, 2))
    story.append(image)
    story.append(Paragraph(caption, styles["caption"]))


def footer(canvas, doc) -> None:
    canvas.saveState()
    canvas.setFont("Times-Roman", 7)
    canvas.drawCentredString(
        letter[0] / 2,
        0.30 * inch,
        f"WOCHAT 2026 submission - Sajak Basnet - page {doc.page}",
    )
    canvas.restoreState()


if __name__ == "__main__":
    main()
