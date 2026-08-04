#!/usr/bin/env python3
from __future__ import annotations

import json
import shutil
import subprocess
import sys
from pathlib import Path

REPO = Path.home() / "Projects/github/modu-inc-website"
WORKTREE = Path("/tmp/modu-public-trust-pages-apply")
BRANCH = "agent/public-trust-pages"


def run(argv: list[str], cwd: Path | None = None) -> subprocess.CompletedProcess[str]:
    return subprocess.run(argv, cwd=cwd, text=True, capture_output=True, check=False)


def page_template(*, title: str, description: str, body: str) -> str:
    return f'''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <meta name="description" content="{description}">
    <meta name="theme-color" content="#0d0f12">
    <link rel="canonical" href="https://moduindustries.ca/{title.casefold().split()[0]}.html">
    <title>{title} — MODU INDUSTRIES LTD.</title>
    <link rel="stylesheet" href="styles.css">
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=DM+Sans:ital,opsz,wght@0,9..40,400;0,9..40,600;0,9..40,700;1,9..40,400&family=JetBrains+Mono:wght@400;500&display=swap" rel="stylesheet">
</head>
<body>
    <a href="#main" class="skip-link">Skip to content</a>
    <header class="site-header" role="banner">
        <div class="container">
            <a href="index.html" class="logo" aria-label="MODU INDUSTRIES LTD. home">Modu Inc.</a>
            <nav class="nav" aria-label="Company">
                <a href="company.html">Company</a>
                <a href="security.html">Security</a>
                <a href="support.html">Support</a>
                <a href="privacy.html">Privacy</a>
                <a href="index.html#contact">Contact</a>
            </nav>
        </div>
    </header>
    <main id="main" role="main">
        <section class="hero" aria-labelledby="page-heading">
            <div class="container">
                <p class="hero-tagline">MODU INDUSTRIES LTD.</p>
                <h1 id="page-heading" class="hero-title">{title}</h1>
                <p class="hero-sub">{description}</p>
            </div>
        </section>
        <section class="section">
            <div class="container">
{body}
            </div>
        </section>
    </main>
    <footer class="site-footer" role="contentinfo">
        <div class="container footer-inner">
            <p class="footer-copy">© MODU INDUSTRIES LTD. · Modu Inc. brand</p>
            <p class="footer-legal"><a href="company.html">Company</a> · <a href="security.html">Security</a> · <a href="support.html">Support</a> · <a href="privacy.html">Privacy</a></p>
        </div>
    </footer>
</body>
</html>
'''


COMPANY_BODY = '''                <h2 class="section-title">Legal identity</h2>
                <p><strong>MODU INDUSTRIES LTD.</strong> is a British Columbia company incorporated on July 25, 2025 under incorporation number <strong>BC1549916</strong>. “Modu Inc.” is an operating brand used by the company.</p>
                <p>Founder and director: <strong>Jason Vetter</strong>. Company domain: <a href="https://moduindustries.ca/">moduindustries.ca</a>.</p>

                <h2 class="section-title">What we are building</h2>
                <p>MODU develops a deterministic, local-first software platform for coordinating auditable AI agents, tools and device workflows across computers, phones and edge systems. The product is in active development. Public descriptions are not claims that every capability is generally available, certified or suitable for every environment.</p>

                <h2 class="section-title">Public evidence</h2>
                <ul class="principles-list">
                    <li>Development repositories and technical work are published selectively through <a href="https://github.com/J2theN1">GitHub</a>.</li>
                    <li>Bounded model and demonstration assets may be published through the <a href="https://huggingface.co/moduindustries">MODU Hugging Face organization</a>.</li>
                    <li>Legal, billing, security and customer records remain separate from public repositories.</li>
                </ul>

                <h2 class="section-title">Company contacts</h2>
                <p>General: <a href="mailto:contact@moduindustries.ca">contact@moduindustries.ca</a><br>
                Support: <a href="mailto:support@moduindustries.ca">support@moduindustries.ca</a><br>
                Security: <a href="mailto:security@moduindustries.ca">security@moduindustries.ca</a></p>'''

SECURITY_BODY = '''                <h2 class="section-title">Security approach</h2>
                <p>MODU is designed around bounded capabilities, explicit authority, verifiable receipts and separation between human credentials, machine credentials and public application surfaces.</p>
                <ul class="principles-list">
                    <li><strong>Least authority:</strong> integrations should receive only the scopes required for their documented job.</li>
                    <li><strong>Secret separation:</strong> passwords, tokens, OTPs, recovery codes and private keys are not intended for public repositories, public logs or company spreadsheets.</li>
                    <li><strong>Verification:</strong> operational work is expected to produce evidence that can be checked rather than relying only on a success message.</li>
                    <li><strong>Private control paths:</strong> owner-authorized terminal and device-control lanes are kept separate from public marketplace applications.</li>
                    <li><strong>Data boundaries:</strong> personal, health, family, company and client information are treated as distinct classes rather than one shared memory pool.</li>
                </ul>

                <h2 class="section-title">Responsible disclosure</h2>
                <p>Send a good-faith security report to <a href="mailto:security@moduindustries.ca">security@moduindustries.ca</a>. Include the affected service, reproduction steps, impact, and a safe way to contact you. Do not include passwords, private keys, personal data or unrelated customer information.</p>
                <p>Please do not conduct denial-of-service testing, social engineering, physical intrusion, persistence, data destruction or testing against third-party systems without their written authorization. A public bug-bounty payment is not promised unless it is agreed in writing before work begins.</p>

                <h2 class="section-title">Current assurance status</h2>
                <p>This page describes working practices and direction. MODU does not use this page to claim SOC 2, ISO 27001, HIPAA, government clearance or another independent certification that has not been formally issued.</p>'''

SUPPORT_BODY = '''                <h2 class="section-title">Contact support</h2>
                <p>Email <a href="mailto:support@moduindustries.ca">support@moduindustries.ca</a> for product, access or account questions. General company enquiries can go to <a href="mailto:contact@moduindustries.ca">contact@moduindustries.ca</a>. Security reports belong at <a href="mailto:security@moduindustries.ca">security@moduindustries.ca</a>.</p>

                <h2 class="section-title">What to include</h2>
                <ul class="principles-list">
                    <li>The product, repository, service or device involved.</li>
                    <li>What you expected and what actually happened.</li>
                    <li>Relevant timestamps, versions and non-secret error text.</li>
                    <li>Steps already attempted and the business impact.</li>
                </ul>
                <p>Do not send passwords, API keys, OTPs, recovery codes, private keys or unrestricted data exports by email.</p>

                <h2 class="section-title">Service expectations</h2>
                <p>Support is currently founder-led and prioritized by severity, contractual commitments and available evidence. This public page does not create a guaranteed response time or service-level agreement. Any binding support terms must appear in the applicable written contract.</p>'''

PRIVACY_BODY = '''                <h2 class="section-title">Scope</h2>
                <p>This notice applies to the public website at <a href="https://moduindustries.ca/">moduindustries.ca</a>. It covers only this public website, not private development systems, client deployments or separately contracted services.</p>

                <h2 class="section-title">Website data</h2>
                <p>The current public website does not provide an account login, payment form or embedded customer database. The published source does not intentionally include a first-party analytics script or advertising tracker.</p>
                <p>Web hosting, DNS and content-delivery providers may process ordinary request information such as IP address, browser or user-agent data, requested path, timestamp and security signals to deliver and protect the site.</p>
                <p>The site loads <strong>Google Fonts</strong>. A visitor’s browser may therefore make requests to Google and disclose standard request metadata under Google’s own terms.</p>

                <h2 class="section-title">Email</h2>
                <p>When you email MODU, the company and its email-routing or delivery providers process the address, message, headers and attachments needed to receive, secure and respond to the communication. Messages may be retained for business records, security, support and legal obligations.</p>
                <p>Do not email passwords, OTPs, recovery codes, private keys or information you are not authorized to disclose.</p>

                <h2 class="section-title">Questions and requests</h2>
                <p>For a question about this public website notice, email <a href="mailto:contact@moduindustries.ca">contact@moduindustries.ca</a>. Security matters should be sent to <a href="mailto:security@moduindustries.ca">security@moduindustries.ca</a>.</p>
                <p>Last updated: August 3, 2026.</p>'''


def main() -> int:
    fetch = run(["git", "-C", str(REPO), "fetch", "-q", "origin", BRANCH])
    if fetch.returncode != 0:
        print(json.dumps({"ok": False, "stage": "fetch", "stderr": fetch.stderr[-1500:]}))
        return fetch.returncode
    if WORKTREE.exists():
        run(["git", "-C", str(REPO), "worktree", "remove", "--force", str(WORKTREE)])
        shutil.rmtree(WORKTREE, ignore_errors=True)
    add = run(["git", "-C", str(REPO), "worktree", "add", "--detach", str(WORKTREE), "FETCH_HEAD"])
    if add.returncode != 0:
        print(json.dumps({"ok": False, "stage": "worktree", "stderr": add.stderr[-1500:]}))
        return add.returncode

    pages = {
        "company.html": page_template(
            title="Company",
            description="Verified company identity and a factual overview of MODU’s current product work.",
            body=COMPANY_BODY,
        ),
        "security.html": page_template(
            title="Security",
            description="Security practices, responsible disclosure and current assurance status.",
            body=SECURITY_BODY,
        ),
        "support.html": page_template(
            title="Support",
            description="How to request help and what information to include without exposing secrets.",
            body=SUPPORT_BODY,
        ),
        "privacy.html": page_template(
            title="Privacy",
            description="A website-scoped privacy notice for moduindustries.ca.",
            body=PRIVACY_BODY,
        ),
    }
    for filename, content in pages.items():
        (WORKTREE / filename).write_text(content, encoding="utf-8")

    index_path = WORKTREE / "index.html"
    index = index_path.read_text(encoding="utf-8")
    old_nav = '''                <a href="#vision">Vision</a>
                <a href="#contact">Contact</a>'''
    new_nav = '''                <a href="#vision">Vision</a>
                <a href="company.html">Company</a>
                <a href="security.html">Security</a>
                <a href="support.html">Support</a>
                <a href="privacy.html">Privacy</a>
                <a href="#contact">Contact</a>'''
    if old_nav not in index:
        raise RuntimeError("expected main navigation anchor block is missing")
    index = index.replace(old_nav, new_nav, 1)

    old_contact = '''                    <p>Email: <a href="mailto:contact@moduindustries.ca">contact@moduindustries.ca</a></p>
                    <p>For partnerships, press, or general inquiries.</p>'''
    new_contact = '''                    <p>General: <a href="mailto:contact@moduindustries.ca">contact@moduindustries.ca</a></p>
                    <p>Support: <a href="mailto:support@moduindustries.ca">support@moduindustries.ca</a></p>
                    <p>Security: <a href="mailto:security@moduindustries.ca">security@moduindustries.ca</a></p>
                    <p>For partnerships, press, product support, security reports, or general inquiries.</p>'''
    if old_contact not in index:
        raise RuntimeError("expected contact block is missing")
    index = index.replace(old_contact, new_contact, 1)

    old_footer = '''            <p class="footer-legal">MODU INDUSTRIES LTD. · Modu Inc. brand</p>'''
    new_footer = '''            <p class="footer-legal">MODU INDUSTRIES LTD. · Modu Inc. brand · <a href="company.html">Company</a> · <a href="security.html">Security</a> · <a href="support.html">Support</a> · <a href="privacy.html">Privacy</a></p>'''
    if old_footer not in index:
        raise RuntimeError("expected footer block is missing")
    index = index.replace(old_footer, new_footer, 1)
    index_path.write_text(index, encoding="utf-8")

    tests = run([sys.executable, "-m", "unittest", "discover", "-s", "tests", "-v"], cwd=WORKTREE)
    if tests.returncode != 0:
        print(json.dumps({"ok": False, "stage": "tests", "stdout": tests.stdout[-5000:], "stderr": tests.stderr[-5000:]}))
        return tests.returncode

    run(["git", "add", "index.html", *pages.keys()], cwd=WORKTREE)
    commit = run(["git", "commit", "-m", "feat: add public company trust pages"], cwd=WORKTREE)
    if commit.returncode != 0:
        print(json.dumps({"ok": False, "stage": "commit", "stdout": commit.stdout[-2000:], "stderr": commit.stderr[-2000:]}))
        return commit.returncode
    push = run(["git", "push", "origin", f"HEAD:{BRANCH}"], cwd=WORKTREE)
    if push.returncode != 0:
        print(json.dumps({"ok": False, "stage": "push", "stdout": push.stdout[-2000:], "stderr": push.stderr[-2000:]}))
        return push.returncode
    result = {
        "ok": True,
        "branch": BRANCH,
        "pages": sorted(pages),
        "tests": tests.stderr.strip().splitlines()[-1] if tests.stderr.strip() else "passed",
        "commit": run(["git", "rev-parse", "HEAD"], cwd=WORKTREE).stdout.strip(),
    }
    print(json.dumps(result, separators=(",", ":")))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
