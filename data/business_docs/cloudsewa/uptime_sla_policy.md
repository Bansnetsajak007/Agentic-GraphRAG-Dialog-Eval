# CloudSewa Uptime and SLA Policy

## 1. SLA Overview

CloudSewa aims to provide reliable hosting and cloud infrastructure. However, uptime guarantees depend on the service plan, infrastructure type, customer configuration, and whether the service is managed or unmanaged.

SLA applies only to eligible paid services and only for CloudSewa-controlled infrastructure.

## 2. Target Uptime

CloudSewa target uptime:

1. Shared Hosting: 99.5% monthly target uptime
2. WordPress Hosting: 99.5% monthly target uptime
3. Business Hosting: 99.9% monthly target uptime
4. VPS Hosting: 99.5% monthly target uptime
5. Managed VPS: 99.9% monthly target uptime
6. DNS Hosting: Best-effort unless premium DNS is purchased

Target uptime is not the same as guaranteed credit eligibility. Credit eligibility requires verification.

## 3. Downtime Definition

Downtime means the service is unavailable due to CloudSewa-controlled infrastructure failure.

Examples of eligible downtime include host node failure, network outage inside CloudSewa infrastructure, storage cluster failure, control panel outage affecting hosted service, datacenter power issue, and CloudSewa firewall misconfiguration.

## 4. Non-Eligible Downtime

SLA credit does not apply to downtime caused by customer code error, customer misconfiguration, DNS misconfiguration by customer, domain expiry, SSL expiry caused by wrong DNS, customer firewall rules, customer deleted files, customer exceeded resource limit, malware or compromised website, scheduled maintenance, emergency security maintenance, DDoS attack outside purchased protection level, third-party provider outage, payment suspension, abuse suspension, or force majeure events.

## 5. Scheduled Maintenance

CloudSewa may perform scheduled maintenance for security patching, hardware replacement, network upgrade, storage maintenance, control panel upgrade, kernel update, and backup system update.

CloudSewa tries to notify customers before planned maintenance whenever possible.

Scheduled maintenance is not counted as SLA downtime if notice is provided.

## 6. Emergency Maintenance

Emergency maintenance may happen without prior notice if required for security vulnerability, active attack, hardware instability, network incident, data corruption prevention, or abuse containment.

Emergency maintenance is handled with minimum required downtime.

## 7. SLA Credit Request

Customers must request SLA credit within 7 days of the incident.

The request must include customer account email, service ID, domain or VPS IP, date and time of outage, description of impact, evidence such as monitoring logs or screenshots, and support ticket reference if available.

CloudSewa will verify outage logs before approving credit.

## 8. SLA Credit Amount

Possible service credit:

1. Downtime below target but under 4 hours: 5% monthly service credit
2. Downtime 4 to 12 hours: 10% monthly service credit
3. Downtime 12 to 24 hours: 25% monthly service credit
4. Downtime above 24 hours: 50% monthly service credit

Service credit is applied to future invoices. It is not paid as cash refund.

## 9. SLA Credit Limit

Maximum SLA credit cannot exceed the monthly fee paid for the affected service.

SLA credit applies only to the affected service, not to unrelated services, lost sales, reputation loss, marketing cost, or business interruption.

## 10. Standard SLA Support Responses

Customer:
"mero site down thiyo, compensation paincha?"

Response:
"SLA credit eligibility outage ko cause, duration, service plan, ra CloudSewa infrastructure logs anusar verify huncha. Kripaya service ID, outage time, ra evidence share garnu hola."

Customer:
"Scheduled maintenance ko lagi credit paincha?"

Response:
"Scheduled maintenance usually SLA credit ma count hudaina, especially notice provide gareko case ma. Tara unexpected extended outage bhaye support team le review garna sakcha."

Customer:
"VPS down thiyo tara mero firewall mistake raicha"

Response:
"Customer firewall, OS, application, or DNS misconfiguration bata bhayeko downtime SLA eligible hudaina. CloudSewa infrastructure issue bhaye matra SLA credit review huncha."
