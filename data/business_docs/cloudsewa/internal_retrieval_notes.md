# CloudSewa Internal Retrieval Notes for RAG Benchmark

## 1. Intended Query Types

This corpus supports customer queries about:

1. VPS activation
2. VPS slow performance
3. Root password lost
4. Managed vs unmanaged VPS
5. Domain expiry
6. Domain recovery
7. DNS propagation
8. Nameserver misconfiguration
9. Email DNS records
10. SSL installation
11. SSL expiry
12. Mixed content
13. Website down
14. SLA credit
15. Billing unpaid after payment
16. Duplicate payment
17. Refund eligibility
18. Backup restore
19. VPS reinstall data loss
20. Website migration
21. Malware infection
22. Phishing suspension
23. Spam complaint
24. Support ticket priority

## 2. Expected Retrieval Patterns

Simple factual query:
"Unmanaged VPS ma nginx setup gardincha?"

Expected document:
`hosting_plans_policy.md`

Expected answer:
Unmanaged VPS includes infrastructure-level support only. OS, web server, database, security setup, and application deployment are customer responsibility. Managed VPS add-on is needed for setup help.

Multi-hop query:
"DNS change garepachi email chalena kina?"

Expected document:
`domain_dns_policy.md`

Expected answer:
Nameserver change may remove old DNS records. Email needs MX, SPF, DKIM, and DMARC records. Ask for domain and current nameserver.

Ambiguous query:
"site down cha"

Expected document:
`support_ticket_incident_sop.md`

Expected behavior:
Ask for domain or service ID. Check hosting status, DNS, invoice, SSL, and server response. Do not assume cause.

SLA query:
"Website 5 ghanta down thiyo credit paincha?"

Expected document:
`uptime_sla_policy.md`

Expected answer:
SLA eligibility depends on outage cause and logs. If CloudSewa-controlled infrastructure downtime is verified, 4 to 12 hours may qualify for 10% monthly service credit. Customer must request within 7 days with evidence.

Domain query:
"Domain expire bhayo recover huncha?"

Expected document:
`domain_dns_policy.md`

Expected answer:
Recovery depends on TLD and registry status. It may be in grace or redemption. Support must check domain status and must not promise recovery before verification.

SSL query:
"SSL expired bhayo"

Expected document:
`ssl_certificate_policy.md`

Expected answer:
Ask for domain. Check SSL status, DNS, validation, hosting status, and certificate error. Production SSL expiry is high priority for managed hosting and business plans.

Backup query:
"VPS reinstall garda data bachcha?"

Expected document:
`backup_restore_migration_policy.md`

Expected answer:
VPS OS reinstall may delete existing data. Customer should take backup or snapshot before reinstall.

## 3. Recommended Metadata Tags

Recommended document metadata:

- company: CloudSewa
- domain: hosting_cloud
- document_type: policy or sop or tone_guide
- language: english_with_romanized_nepali_examples
- version: v1.0

## 4. Benchmark Importance

This company is useful for testing whether the RAG system can handle technical troubleshooting, responsibility boundary between provider and customer, multi-hop DNS and email reasoning, SLA eligibility reasoning, domain expiry uncertainty, support escalation, missing-information detection, policy-grounded refusal, and Romanized Nepali technical support.

## 5. Traditional Semantic RAG Weaknesses to Observe

Traditional Semantic RAG may struggle with distinguishing managed vs unmanaged VPS support scope, knowing when to ask for service ID instead of answering directly, correctly reasoning about DNS plus email failure, handling SLA credit eligibility with exclusions, avoiding false promise in domain recovery, avoiding hallucinated exact fix time during outage, mapping short Romanized Nepali queries like "site chalena" to incident workflow, and understanding that backup availability depends on plan and retention.
