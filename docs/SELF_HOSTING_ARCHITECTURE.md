# MODU public-site architecture

## Decision

Keep the public corporate site in this repository and serve it through GitHub Pages. Use a domain registrar only to hold the domain registration. DNS, TLS, deployment, source control, backups, and monitoring remain independent of GoDaddy hosting or its website builder.

## Current hosting

- Repository: `J2theN1/modu-inc-website`
- Publishing source: `main` branch, repository root
- Canonical public origin: `https://moduindustries.ca/`
- Rollback origin: `https://j2then1.github.io/modu-inc-website/`
- Registrar: Cloudflare Registrar
- DNS provider: Cloudflare
- DNS mode during certificate issuance: DNS-only
- HTTPS: GitHub Pages certificate provisioning is monitored automatically; enforcement is enabled only after the certificate covers both the apex and `www` names

## Current domain configuration

- Apex: all four current GitHub Pages A records
- Apex: all four current GitHub Pages AAAA records
- `www`: CNAME to `j2then1.github.io`
- GitHub Pages custom domain: `moduindustries.ca`
- Canonical metadata: `https://moduindustries.ca/`
- `www` redirects to the apex through GitHub Pages
- No wildcard DNS record
- No home IP, residential router port, or self-hosted mail server is exposed

## Cutover verification

1. Confirm the domain remains present in Cloudflare Registrar inventory.
2. Confirm the CIRA registration and registrant-contact notices.
3. Confirm the exact A, AAAA, and `www` CNAME records remain DNS-only while GitHub provisions TLS.
4. Keep the custom domain attached to the GitHub Pages repository.
5. Keep the scheduled HTTPS-enforcement workflow enabled. It applies `https_enforced=true` only after GitHub reports an approved certificate covering both `moduindustries.ca` and `www.moduindustries.ca`.
6. Run the domain health probe after HTTPS enforcement and require successful DNS, redirect, certificate, apex, and `www` checks.
7. Verify the domain at the GitHub account level with the retained TXT challenge record to reduce takeover risk.
8. Preserve the GitHub Pages origin as a rollback route until the HTTPS health probe passes.

## What remains independent

- Website code and history: GitHub repository
- Hosting and TLS: GitHub Pages
- DNS and registration: Cloudflare, replaceable independently of the site code
- Business email: separate mail provider; do not run mail from the home connection
- Backups: Git plus mirrored repository/archive
- Monitoring: scheduled GitHub Actions and external DNS/HTTPS checks

## Designs rejected for the corporate landing page

- Direct home-PC hosting: unnecessary exposure, uptime dependency, residential-IP and router risk.
- Direct router port forwarding: not required for a static site.
- GoDaddy website builder/hosting: adds cost and lock-in without benefiting this static repository.

A home server or outbound tunnel remains appropriate for authenticated internal tools and demos, not for the primary public corporate landing page.
