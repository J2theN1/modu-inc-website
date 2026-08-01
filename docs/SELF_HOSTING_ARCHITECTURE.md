# MODU public-site architecture

## Decision

Keep the public corporate site in this repository and serve it through GitHub Pages. Use a domain registrar only to hold the domain registration. DNS, TLS, deployment, source control, backups, and monitoring remain independent of GoDaddy hosting or its website builder.

## Current hosting

- Repository: `J2theN1/modu-inc-website`
- Publishing source: `main` branch, repository root
- Public origin: `https://j2then1.github.io/modu-inc-website/`
- HTTPS: enforced by GitHub Pages

## Domain cutover after registration

1. Register the chosen domain with a CIRA-certified registrar.
2. Keep registrar lock, account MFA, auto-renew, and DNSSEC enabled.
3. Add the chosen custom domain in GitHub Pages settings before changing DNS.
4. Configure the registrar/DNS provider with GitHub Pages records:
   - `www`: CNAME to `j2then1.github.io`
   - apex: GitHub Pages A/AAAA records from the current GitHub documentation
5. Verify the domain in GitHub and enable HTTPS.
6. Test apex, `www`, redirects, certificate issuance, and rollback before announcing the domain.

Do not add a `CNAME` file until the domain is actually registered and the exact canonical hostname is approved.

## What remains independent

- Website code and history: GitHub repository
- Hosting and TLS: GitHub Pages
- DNS: registrar DNS or a dedicated DNS provider
- Business email: separate mail provider; do not run mail from the home connection
- Backups: Git plus mirrored repository/archive
- Monitoring: external HTTPS and DNS checks

## Designs rejected for the corporate landing page

- Direct home-PC hosting: unnecessary exposure, uptime dependency, residential-IP and router risk.
- Direct router port forwarding: not required for a static site.
- GoDaddy website builder/hosting: adds cost and lock-in without benefiting this static repository.

A home server or outbound tunnel remains appropriate for authenticated internal tools and demos, not for the primary public corporate landing page.
