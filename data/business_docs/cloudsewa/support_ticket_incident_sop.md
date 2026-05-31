# CloudSewa Support Ticket and Incident Handling SOP

## 1. Ticket Categories

CloudSewa support tickets are categorized as technical support, billing support, domain support, DNS support, SSL support, VPS support, migration support, backup restore, abuse/security, sales inquiry, SLA claim, and account verification.

## 2. Priority Levels

### P1 Critical

Examples:

1. Production server down
2. Website completely unreachable for business hosting
3. Managed VPS unreachable
4. Active security compromise
5. Phishing or malware abuse report
6. Email completely down for business account
7. Data loss incident

Target first response: 15 minutes during active support hours
Escalation: immediate

### P2 High

Examples:

1. SSL expired on production website
2. DNS misconfiguration causing outage
3. VPS performance severe degradation
4. Payment completed but service not activated
5. Backup restore needed urgently
6. Domain expired recently

Target first response: 30 minutes to 1 hour

### P3 Normal

Examples:

1. Plugin issue guidance
2. DNS record update request
3. Plan upgrade
4. Migration scheduling
5. Email account setup
6. General VPS question

Target first response: 4 business hours

### P4 Low

Examples:

1. General inquiry
2. Feature request
3. Documentation clarification
4. Non-urgent sales question
5. UI navigation help

Target first response: 1 business day

## 3. Ticket Information Requirements

Support should collect service ID, domain name or VPS IP, customer account email, issue description, screenshot or error message, time issue started, recent changes made, login access if required, whether issue affects production, and business impact.

## 4. Server Down Workflow

If customer says server is down, check service status, invoice status, suspension status, node status, network status, DNS status, ping response, HTTP response, SSH access, and recent maintenance notice.

If CloudSewa infrastructure issue is found, escalate to infrastructure team.

If customer-side issue is found, explain clearly.

## 5. DNS Issue Workflow

Ask domain name, current nameservers, record changed, old value, new value, time of change, and service affected: website, email, SSL, app, or API.

Check whether DNS record exists, DNS value is correct, nameservers are correct, TTL/propagation, domain expiry, and DNSSEC issue if applicable.

## 6. SSL Issue Workflow

Ask domain name, SSL error screenshot, whether DNS recently changed, whether domain points to CloudSewa, and whether Cloudflare or proxy is used.

Check certificate expiry, certificate common name, chain validity, DNS record, HTTP validation path, mixed content, and redirect loop.

## 7. Billing Issue Workflow

Ask invoice number, payment method, transaction ID, payment screenshot, amount, and date and time.

Check invoice status, gateway status, duplicate payment, manual bank verification, and service activation status.

## 8. Incident Communication

During infrastructure incident, support should provide acknowledgement, affected service, current investigation status, workaround if available, next update time, and final resolution summary after recovery.

Do not provide fake ETA.

Use:
"Our infrastructure team is investigating. Next update will be shared within 30 minutes."

Avoid:
"It will be fixed in 5 minutes" unless engineering confirms it.

## 9. Ticket Closure

Ticket can be closed when customer confirms resolution, issue is fixed and customer is informed, required details were not provided after follow-up period, billing correction is completed, abuse case is resolved, migration is completed, or restore is completed.

For unresolved critical cases, do not close without escalation note.

## 10. Escalation Note Format

```text
Ticket ID:
Customer account:
Service ID:
Domain/VPS IP:
Issue category:
Priority:
Customer impact:
Steps already checked:
Evidence attached:
Recommended escalation team:
Urgency reason:
```

## 11. Standard Ticket Responses

Customer:
"Website open nai hudaina"

Response:
"Kripaya domain name or service ID share garnu hola. Ma hosting status, DNS, invoice status, SSL, ra server response check garera issue CloudSewa side ho ki configuration side ho verify garchu."

Customer:
"Server down cha, urgent"

Response:
"Sorry for the impact. Kripaya VPS ID or IP share garnu hola. Ma immediately infrastructure status check garera required bhaye engineering team ma escalate garchu."

Customer:
"Ticket reply kahile aucha?"

Response:
"Ticket priority anusar response time farak huncha. Critical production outage highest priority ma handle huncha. Kripaya ticket ID share garnu hola, ma status check garna help garchu."
