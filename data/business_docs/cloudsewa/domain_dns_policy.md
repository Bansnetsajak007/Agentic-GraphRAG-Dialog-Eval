# CloudSewa Domain and DNS Policy

## 1. Domain Registration

CloudSewa allows customers to register domain names through supported registries.

Domain registration is subject to domain availability, registry rules, customer information accuracy, payment confirmation, verification requirements, and TLD-specific restrictions.

CloudSewa cannot guarantee domain availability until registration is completed successfully.

## 2. Domain Renewal

Customers are responsible for renewing domains before expiry.

CloudSewa sends renewal reminders by email and dashboard notification when possible.

Typical reminder schedule:

1. 30 days before expiry
2. 15 days before expiry
3. 7 days before expiry
4. 1 day before expiry
5. On expiry date

Failure to receive reminder does not remove customer responsibility to renew the domain.

## 3. Expired Domain

When a domain expires, website may stop working, email may stop working, DNS changes may be disabled, renewal price may change, late renewal fee may apply, and domain may enter grace or redemption period depending on TLD.

CloudSewa cannot guarantee recovery of expired domains after the allowed recovery period.

## 4. Redemption Period

Some domains may enter redemption period after expiry and deletion process.

During redemption, domain may not work, recovery may require additional fee, recovery may take time, registry rules apply, and not all domains are recoverable.

Support must not promise domain recovery until registry status is confirmed.

## 5. Domain Transfer to CloudSewa

To transfer a domain to CloudSewa, customer may need domain unlocked, authorization code or EPP code, valid admin email access, no transfer lock, domain older than required minimum period, no active dispute, and payment for transfer if required.

Domain transfer may take several hours to several days depending on registry.

## 6. Domain Transfer Away

Customer may transfer domain away from CloudSewa if account is verified, domain is active, domain is not locked due to abuse or dispute, invoice is cleared, EPP code is requested, and registry transfer rules allow transfer.

CloudSewa may deny or delay transfer if domain is under investigation, unpaid, or legally restricted.

## 7. DNS Management

DNS records control how a domain points to hosting, email, and other services.

Common DNS record types:

1. A record
2. AAAA record
3. CNAME record
4. MX record
5. TXT record
6. SPF record
7. DKIM record
8. DMARC record
9. NS record
10. SRV record

Customers must configure DNS carefully. Wrong DNS records may break website, email, SSL verification, or third-party services.

## 8. DNS Propagation

DNS changes may take time to update across global resolvers.

Propagation time depends on TTL value, ISP resolver cache, nameserver change, registry update time, local DNS cache, and browser cache.

Typical DNS record changes may update within minutes to a few hours, but nameserver changes can take longer.

Support should not promise instant DNS propagation.

## 9. Nameserver Change

If customer changes nameservers, all DNS records should be recreated or imported into the new DNS provider.

Common issue: customer changes nameserver but forgets to add MX records, causing email failure.

Support should always ask which nameservers are currently active, where DNS is hosted, which service is not working, what DNS record was changed, and when it was changed.

## 10. Email DNS Records

For email hosting, customer may need MX record, SPF record, DKIM record, DMARC record, and Webmail CNAME or A record.

Wrong MX records can stop receiving emails.

Wrong SPF/DKIM/DMARC can cause email deliverability problems.

## 11. Standard DNS Support Responses

Customer:
"DNS change gareko, website ajhai open vayena"

Response:
"DNS propagation time lagna sakcha. Kripaya domain name, changed record, old value, new value, ra change gareko time share garnu hola. Ma records check garna help garchu."

Customer:
"Nameserver change garepachi email chalena"

Response:
"Nameserver change garda old DNS records copy nahuda email stop huna sakcha. Kripaya domain ra current nameserver share garnu hola. MX, SPF, DKIM, DMARC records verify garna parcha."

Customer:
"Domain expire bhayo, recover huncha?"

Response:
"Domain recovery TLD ra current registry status anusar depend garcha. Kripaya domain name share garnu hola, ma active, grace, redemption, or deleted status check garna help garchu."
