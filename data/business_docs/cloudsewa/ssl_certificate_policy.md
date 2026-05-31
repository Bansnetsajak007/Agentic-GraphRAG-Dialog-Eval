# CloudSewa SSL Certificate Policy

## 1. SSL Overview

SSL certificates enable HTTPS for websites.

CloudSewa supports free SSL certificates where available, AutoSSL for supported hosting plans, paid SSL certificates, wildcard SSL for selected domains, SSL installation support, SSL renewal support, and SSL troubleshooting.

## 2. Free SSL

Free SSL may be available for hosting accounts using CloudSewa nameservers or properly configured DNS.

Free SSL requires domain pointing to correct server, valid DNS records, HTTP or DNS validation success, no conflicting certificate, no blocked validation path, and active hosting account.

## 3. SSL Validation Methods

SSL may be validated through HTTP validation, DNS validation, or email validation for selected paid certificates.

If validation fails, certificate cannot be issued.

## 4. Common SSL Failure Reasons

SSL setup may fail due to domain not pointing to CloudSewa server, DNS propagation incomplete, wrong A record, wrong CNAME record, Cloudflare proxy conflict, HTTP validation blocked, website redirect loop, firewall blocking validation, domain suspended or expired, or too many failed certificate requests.

## 5. SSL Renewal

Free SSL certificates usually renew automatically if hosting account is active, domain still points correctly, DNS validation passes, HTTP validation path is accessible, and no major DNS misconfiguration exists.

Customer should open support ticket if SSL is near expiry and not renewed.

## 6. Expired SSL

If SSL expires, browser may show security warning, customers may lose trust, checkout pages may fail, APIs may reject requests, and SEO and analytics may be affected.

Production SSL expiry is treated as high priority for managed hosting and business plans.

## 7. Wildcard SSL

Wildcard SSL covers subdomains such as app.example.com, api.example.com, and blog.example.com.

Wildcard SSL usually requires DNS validation.

Wildcard SSL may not be included in basic hosting plans.

## 8. SSL for External Hosting

If customer domain is hosted elsewhere, CloudSewa can provide guidance only if DNS or certificate is managed through CloudSewa.

If website is hosted on third-party infrastructure, customer may need to contact that hosting provider.

## 9. Mixed Content Issue

A website may have SSL installed but still show "Not Secure" due to mixed content.

Mixed content means the page loads some resources through HTTP instead of HTTPS.

Examples include images using HTTP links, CSS files using HTTP links, JavaScript files using HTTP links, API calls using HTTP links, and hardcoded old URLs in WordPress database.

CloudSewa can guide customer but custom website code fixes may not be included in basic support.

## 10. Standard SSL Support Responses

Customer:
"SSL expired bhayo"

Response:
"Kripaya domain name share garnu hola. Ma SSL status check garera renewal issue DNS, validation, hosting status, or certificate error bata ho ki verify garna help garchu."

Customer:
"HTTPS chalcha tara not secure dekhaucha"

Response:
"SSL install bhayepani mixed content issue huna sakcha. Page le HTTP image, CSS, JS, or API load gareko cha bhane browser le not secure dekhauna sakcha."

Customer:
"Free SSL install garna milcha?"

Response:
"Free SSL available huna domain correct server ma point vako, hosting active vako, ra validation pass vako hunu parcha. Kripaya domain share garnu hola, ma eligibility check garna help garchu."
