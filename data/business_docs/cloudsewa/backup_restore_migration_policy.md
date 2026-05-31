# CloudSewa Backup, Restore, and Migration Policy

## 1. Backup Overview

CloudSewa encourages all customers to maintain their own backups.

CloudSewa may provide backup tools or managed backup depending on plan, but customer remains responsible for critical data protection unless a managed backup service is purchased.

## 2. Backup Types

CloudSewa may support cPanel account backup, website file backup, database backup, email backup, VPS snapshot, managed backup add-on, manual backup before migration, and offsite backup for selected plans.

## 3. Backup Frequency

Backup frequency depends on plan.

Example backup schedule:

1. Basic shared hosting: weekly best-effort backup
2. Business hosting: daily backup with limited retention
3. WordPress managed hosting: daily backup
4. Unmanaged VPS: no automatic backup unless add-on purchased
5. Managed VPS: backup schedule according to selected package

Backup availability is not guaranteed unless the customer has paid backup add-on.

## 4. Backup Retention

Retention may depend on plan:

1. Weekly backup: retained up to 7 days
2. Daily backup: retained up to 14 days
3. Managed backup: retained according to contract
4. VPS snapshot: retained until customer deletes or plan expires

CloudSewa may delete old backups automatically to manage storage.

## 5. Restore Request

Customer may request restore by providing service ID, domain name, restore date, files/database/email to restore, reason for restore, and confirmation that current data may be overwritten.

Restore may overwrite current files and databases. Support must warn customer before restore.

## 6. Restore Limitations

Restore may not be possible if no backup exists, backup is corrupted, backup retention expired, service was terminated, account was suspended for abuse, backup storage failed, customer deleted data before backup point, or customer wants a date not available.

CloudSewa does not guarantee recovery unless managed backup plan explicitly guarantees it.

## 7. Customer-Owned Backup

Customers should keep independent backups before website update, plugin update, theme update, application deployment, database migration, DNS migration, server upgrade, cancellation, OS reinstall, or major configuration change.

## 8. Migration Support

CloudSewa may help migrate websites from another provider.

Migration may include website files, database, email accounts where possible, DNS guidance, SSL setup, WordPress migration, cPanel to cPanel transfer, and basic verification after migration.

Migration support does not include fixing broken source website, rebuilding website, custom code rewrite, SEO repair, third-party plugin license transfer, large custom application deployment without managed service, or fixing malware before migration unless cleanup is purchased.

## 9. Migration Requirements

Customer must provide old hosting login, cPanel or FTP access, database access if needed, WordPress admin if needed, domain registrar access or DNS access, email migration details, preferred migration time, and confirmation of backup.

CloudSewa is not responsible for migration delay if customer provides wrong or incomplete credentials.

## 10. Migration Downtime

Migration may involve temporary downtime due to DNS propagation, database copy, email record changes, SSL reissue, large file transfer, source server speed, and application compatibility.

CloudSewa tries to reduce downtime but cannot guarantee zero downtime for all migrations.

## 11. Standard Backup and Migration Responses

Customer:
"Website delete bhayo, restore garna milcha?"

Response:
"Restore availability backup plan, backup date, ra retention anusar depend garcha. Kripaya service ID, domain, ra kun date ko restore chaiyeko ho share garnu hola."

Customer:
"VPS reinstall garda data bachcha?"

Response:
"VPS OS reinstall garda existing data delete huna sakcha. Reinstall garnu aghi backup or snapshot lina strongly recommend garincha."

Customer:
"Old hosting bata CloudSewa ma migrate gardinu huncha?"

Response:
"Migration support available cha. Kripaya old hosting access, domain, database details, email migration need, ra preferred migration time share garnu hola."
