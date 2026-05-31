# ChitoMart Internal Retrieval Notes for RAG Benchmark

## 1. Intended Query Types

This corpus is designed to support the following customer query types:

1. Delivery charge questions
2. Delivery time questions
3. Free delivery threshold questions
4. Refund eligibility questions
5. Damaged item complaints
6. Wrong item complaints
7. Missing item complaints
8. Payment deducted but order failed
9. Coupon not working
10. Product availability
11. Substitution approval
12. Cancellation request
13. Refund delay
14. Rider complaint
15. COD restriction
16. Account/address change
17. Complaint escalation

## 2. Expected Retrieval Patterns

Simple factual query:
"Baneshwor ma delivery charge kati ho?"

Expected document:
`delivery_policy.md`

Expected fact:
Baneshwor belongs to Kathmandu Central Zone, standard delivery charge NPR 60, free delivery threshold NPR 1,500.

Multi-hop query:
"Baneshwor ma 1500 ko order garda delivery free huncha?"

Expected document:
`delivery_policy.md`

Expected facts:
Baneshwor is Kathmandu Central Zone.
Kathmandu Central Zone free delivery threshold is NPR 1,500.
Order amount NPR 1,500 qualifies.

Ambiguous query:
"refund chahiyo"

Expected document:
`refund_return_policy.md`

Expected behavior:
Ask for order ID and refund reason. Do not approve refund without details.

Payment query:
"payment katyo tara order place vayena"

Expected document:
`payment_billing_policy.md`

Expected facts:
Collect transaction ID, screenshot, deducted amount, payment method, phone number. Escalate to payment team. Resolution 1 to 3 business days, complex cases up to 5 business days.

Complaint query:
"service dherai slow cha"

Expected document:
`complaint_handling_sop.md`

Expected behavior:
Apologize, ask for order ID, check delay reason, update customer.

Coupon query:
"coupon apply bhayena"

Expected document:
`promotions_coupon_policy.md`

Expected facts:
Check coupon spelling, expiry, minimum order amount, category eligibility, payment method, area, and usage limit.

## 3. Useful Metadata Tags

When indexing these documents, recommended metadata:

- company: ChitoMart
- domain: quick_commerce
- document_type: policy or sop or tone_guide
- language: english_with_romanized_nepali_examples
- version: v1.0

## 4. Important Benchmark Note

The RAG system should not answer from general world knowledge. It should answer using this ChitoMart corpus only.

If retrieved context does not contain the answer, the system should say that more details are needed or that the information is not available in the provided company policy.

## 5. Baseline Limitation

Traditional Semantic RAG may struggle with ambiguous customer queries, multi-hop area plus threshold questions, payment issue requiring structured form collection, complaint priority classification, coupon restriction reasoning, and cases requiring clarification before answering.

These limitations are useful for later comparison with Agentic RAG and Agentic GraphRAG.
