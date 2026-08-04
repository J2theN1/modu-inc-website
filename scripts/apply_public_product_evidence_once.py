from __future__ import annotations

from pathlib import Path
from textwrap import dedent


ROOT = Path(__file__).resolve().parents[1]
ORIGIN = "https://moduindustries.ca"

NAV = """
<nav class="nav" aria-label="Main navigation">
    <a href="product.html">Product</a>
    <a href="evidence.html">Evidence</a>
    <a href="pitch-deck.html">Pitch</a>
    <a href="company.html">Company</a>
    <a href="security.html">Security</a>
    <a href="support.html">Support</a>
    <a href="privacy.html">Privacy</a>
    <a href="index.html#contact">Contact</a>
</nav>
""".strip()

FOOTER = """
<footer class="site-footer" role="contentinfo">
    <div class="container footer-inner">
        <p class="footer-copy">MODU INDUSTRIES LTD. · Modu Inc. operating brand</p>
        <p class="footer-legal"><a href="product.html">Product</a> · <a href="evidence.html">Evidence</a> · <a href="pitch-deck.html">Pitch</a> · <a href="company.html">Company</a> · <a href="security.html">Security</a> · <a href="support.html">Support</a> · <a href="privacy.html">Privacy</a></p>
        <p class="footer-legal">West Kelowna, British Columbia, Canada · <a href="mailto:contact@moduindustries.ca">contact@moduindustries.ca</a></p>
    </div>
</footer>
""".strip()


def canonical(path: str) -> str:
    return f"{ORIGIN}/" if path == "index.html" else f"{ORIGIN}/{path}"


def render_page(
    *,
    path: str,
    title: str,
    description: str,
    body: str,
    extra_head: str = "",
) -> str:
    url = canonical(path)
    return dedent(
        f"""\
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <meta name="description" content="{description}">
            <meta name="theme-color" content="#0b0f14">
            <meta name="robots" content="index, follow">
            <link rel="canonical" href="{url}">
            <meta property="og:title" content="{title}">
            <meta property="og:description" content="{description}">
            <meta property="og:type" content="website">
            <meta property="og:url" content="{url}">
            <meta property="og:site_name" content="Modu Inc.">
            <title>{title}</title>
            <link rel="stylesheet" href="styles.css">
            {extra_head}
        </head>
        <body>
            <a href="#main" class="skip-link">Skip to content</a>
            <header class="site-header" role="banner">
                <div class="container header-inner">
                    <a href="index.html" class="logo" aria-label="MODU INDUSTRIES LTD. home"><span class="logo-mark">M</span><span>Modu Inc.</span></a>
                    {NAV}
                </div>
            </header>
            <main id="main" role="main">
                {body.strip()}
            </main>
            {FOOTER}
        </body>
        </html>
        """
    )


HOME_BODY = """
<section class="hero hero-home" aria-labelledby="hero-heading">
    <div class="container hero-grid">
        <div>
            <p class="eyebrow">Local-first · governed · verifiable</p>
            <h1 id="hero-heading">AI and device orchestration for work that must actually finish.</h1>
            <p class="hero-lead">MODU is a local-first AI and device-orchestration platform for auditable work across computers, phones, models, and connected services.</p>
            <p class="status-line"><span class="status-dot" aria-hidden="true"></span><strong>Current stage:</strong> active research and development, early validation, not generally available.</p>
            <div class="button-row">
                <a class="btn btn-primary" href="product.html">Explore the product</a>
                <a class="btn btn-secondary" href="evidence.html">Review public evidence</a>
            </div>
        </div>
        <aside class="hero-panel" aria-label="MODU execution model">
            <p class="panel-label">Execution model</p>
            <ol class="flow-list">
                <li><span>01</span><strong>Authorize</strong><small>Bind the goal, identity, scope, and consequences.</small></li>
                <li><span>02</span><strong>Execute</strong><small>Use the right connected app, local worker, or bounded browser action.</small></li>
                <li><span>03</span><strong>Verify</strong><small>Capture receipts and check the real result before claiming success.</small></li>
                <li><span>04</span><strong>Resume</strong><small>Pause for human-only gates without losing workflow state.</small></li>
            </ol>
        </aside>
    </div>
</section>

<section class="section" id="product">
    <div class="container">
        <div class="section-heading">
            <p class="eyebrow">Product</p>
            <h2>One governed runtime across many execution surfaces.</h2>
            <p>Large language models are reasoning components inside MODU—not the entire system. Procedures, permissions, tools, memory, devices, and receipts remain explicit parts of the product.</p>
        </div>
        <div class="card-grid four-up">
            <article class="card"><h3>Governed workflows</h3><p>Actions are constrained by identity, authority, allowed origins, consequence class, duplicate guards, and completion criteria.</p></article>
            <article class="card"><h3>Local-first compute</h3><p>Capable local CPUs, GPUs, and device accelerators can do useful work without making metered cloud inference the default.</p></article>
            <article class="card"><h3>Cross-device execution</h3><p>Computers, phones, connected services, and professional software can participate as bounded workers in one workflow.</p></article>
            <article class="card"><h3>Result-bound verification</h3><p>Operations produce evidence tied to the worker, adapter, action, and observed result rather than an unverified success message.</p></article>
        </div>
        <p class="section-link"><a href="product.html">Read the product boundary and architecture →</a></p>
    </div>
</section>

<section class="section section-alt" id="evidence">
    <div class="container">
        <div class="section-heading">
            <p class="eyebrow">Working evidence</p>
            <h2>Public proof is separated from private operational state.</h2>
            <p>The site links to selected public source, company identity, security practices, technical narrative, and current limitations. Private credentials, device addresses, customer data, and internal queues are deliberately excluded.</p>
        </div>
        <div class="evidence-list">
            <a class="evidence-item" href="https://github.com/J2theN1"><span>Public source</span><strong>Selected repositories and development history</strong><em>GitHub ↗</em></a>
            <a class="evidence-item" href="pitch-deck.html"><span>Technical narrative</span><strong>Architecture, problem, current stage, and acceleration needs</strong><em>Pitch deck →</em></a>
            <a class="evidence-item" href="company.html"><span>Company identity</span><strong>British Columbia incorporation and public company contacts</strong><em>Company →</em></a>
            <a class="evidence-item" href="security.html"><span>Trust boundary</span><strong>Authority, secret separation, verification, and disclosure practices</strong><em>Security →</em></a>
        </div>
        <p class="section-link"><a href="evidence.html">See the complete public evidence index →</a></p>
    </div>
</section>

<section class="section" id="architecture">
    <div class="container">
        <div class="section-heading">
            <p class="eyebrow">Architecture</p>
            <h2>Designed for recovery, not perfect first attempts.</h2>
            <p>MODU treats CAPTCHA, MFA, legal terms, payments, unavailable devices, and changing web pages as explicit workflow states. The system records what happened and resumes from bounded state instead of restarting blindly.</p>
        </div>
        <div class="architecture-strip" aria-label="MODU architecture stages">
            <div><span>Context</span><strong>Identity · evidence · policy</strong></div>
            <div><span>Planning</span><strong>One exact next action</strong></div>
            <div><span>Workers</span><strong>Apps · PC · phones · browser</strong></div>
            <div><span>Receipts</span><strong>Observed result · durable state</strong></div>
        </div>
    </div>
</section>

<section class="section section-alt" id="stage">
    <div class="container two-column">
        <div>
            <p class="eyebrow">Current stage</p>
            <h2>Founder-funded R&amp;D moving toward bounded pilots.</h2>
        </div>
        <div class="prose">
            <p>The company has active software, bridge, device, browser-workflow, and local-model development. The present objective is to turn that infrastructure into a focused, repeatable product with measurable pilot outcomes.</p>
            <p>This website does not claim general availability, recurring revenue, independent certification, or suitability for regulated production use.</p>
            <div class="button-row">
                <a class="btn btn-secondary" href="pitch-deck.html">View the pitch deck</a>
                <a class="btn btn-secondary" href="company.html">Verify the company</a>
            </div>
        </div>
    </div>
</section>

<section class="section" id="contact">
    <div class="container contact-panel">
        <div>
            <p class="eyebrow">Contact</p>
            <h2>Discuss technical review, startup support, or a bounded pilot.</h2>
            <p>MODU INDUSTRIES LTD. · West Kelowna, British Columbia, Canada</p>
        </div>
        <a class="btn btn-primary" href="mailto:contact@moduindustries.ca">contact@moduindustries.ca</a>
    </div>
</section>
"""

HOME_STRUCTURED_DATA = """
<script type="application/ld+json">
{
  "@context": "https://schema.org",
  "@type": "Organization",
  "name": "Modu Inc.",
  "legalName": "MODU INDUSTRIES LTD.",
  "url": "https://moduindustries.ca/",
  "email": "contact@moduindustries.ca",
  "foundingDate": "2025-07-25",
  "foundingLocation": {
    "@type": "Place",
    "address": {
      "@type": "PostalAddress",
      "addressLocality": "West Kelowna",
      "addressRegion": "British Columbia",
      "addressCountry": "CA"
    }
  },
  "sameAs": [
    "https://github.com/J2theN1",
    "https://huggingface.co/moduindustries"
  ]
}
</script>
""".strip()

PRODUCT_BODY = """
<section class="page-hero" aria-labelledby="page-heading">
    <div class="container">
        <p class="eyebrow">Product</p>
        <h1 id="page-heading">A control layer for agents, tools, devices, and connected services.</h1>
        <p class="hero-lead">MODU coordinates work through explicit procedures, bounded authority, durable state, and verifiable execution.</p>
        <div class="status-badge">Active R&amp;D · early validation · not generally available</div>
    </div>
</section>

<section class="section">
    <div class="container">
        <div class="section-heading"><p class="eyebrow">Product boundary</p><h2>What MODU is—and what it is not.</h2></div>
        <div class="comparison-grid">
            <article class="card"><h3>MODU is</h3><ul class="check-list"><li>A governed workflow runtime</li><li>A local-first execution and orchestration layer</li><li>A bridge between models, tools, apps, PCs, and phones</li><li>A receipt and recovery system for consequential work</li></ul></article>
            <article class="card"><h3>MODU is not presented as</h3><ul class="plain-list"><li>A generally available consumer assistant</li><li>A replacement for legal, medical, or regulated professionals</li><li>A certified compliance platform</li><li>A claim that every experimental capability is production-ready</li></ul></article>
        </div>
    </div>
</section>

<section class="section section-alt">
    <div class="container">
        <div class="section-heading"><p class="eyebrow">Core system</p><h2>Four product components.</h2></div>
        <div class="card-grid two-up">
            <article class="card"><p class="card-number">01</p><h3>Governed workflows</h3><p>Each workflow has a goal, identity references, allowed origins, authority policy, duplicate guard, completion criteria, and durable journal. Reversible work can advance automatically while legal, identity, financial, and destructive consequences remain explicit.</p></article>
            <article class="card"><p class="card-number">02</p><h3>Local and heterogeneous compute</h3><p>The platform can schedule work across local CPU/GPU resources, phones, device accelerators, and selectively used cloud services. Resource choice is part of the procedure rather than hidden behind one provider.</p></article>
            <article class="card"><p class="card-number">03</p><h3>Cross-device execution</h3><p>Connected apps are used directly where available. Local workers, SSH, browser sessions, queues, and device bridges handle work that requires owner-controlled machines or interfaces.</p></article>
            <article class="card"><p class="card-number">04</p><h3>Result-bound verification</h3><p>Execution evidence ties actions to operation IDs, workers, adapters, page or command state, and observed outcomes. Human-only gates can pause and resume without silently replaying earlier writes.</p></article>
        </div>
    </div>
</section>

<section class="section">
    <div class="container">
        <div class="section-heading"><p class="eyebrow">Current work</p><h2>Where the platform is being exercised.</h2></div>
        <div class="tag-grid">
            <span>Code and system audits</span><span>Connected-service workflows</span><span>Persistent browser automation</span><span>Local-model orchestration</span><span>PC and phone workers</span><span>Unreal and Blender workflows</span><span>Knowledge and memory infrastructure</span><span>Company enrolment operations</span>
        </div>
        <p class="note">These are active development areas, not a statement that each is packaged, supported, or sold as a standalone product.</p>
    </div>
</section>

<section class="section section-alt">
    <div class="container two-column">
        <div><p class="eyebrow">Next milestone</p><h2>From infrastructure to repeatable pilots.</h2></div>
        <div class="prose"><p>The immediate product goal is to select bounded workflows, define measurable completion criteria, package the required worker capabilities, and validate cost, reliability, security, and operator experience in controlled pilots.</p><p><a href="evidence.html">Review public evidence →</a></p></div>
    </div>
</section>
"""

EVIDENCE_BODY = """
<section class="page-hero" aria-labelledby="page-heading">
    <div class="container">
        <p class="eyebrow">Evidence</p>
        <h1 id="page-heading">A public index of what can be checked today.</h1>
        <p class="hero-lead">Public evidence is intentionally bounded. It supports the company and product narrative without publishing private credentials, internal infrastructure, personal records, or customer data.</p>
    </div>
</section>

<section class="section">
    <div class="container evidence-sections">
        <article class="evidence-block"><p class="card-number">01</p><div><h2>Company identity</h2><p>MODU INDUSTRIES LTD. is a British Columbia company incorporated July 25, 2025 under incorporation number BC1549916. The company page records the legal identity, founder/director, domain, and public contact routes.</p><p><a href="company.html">Company identity →</a></p></div></article>
        <article class="evidence-block"><p class="card-number">02</p><div><h2>Public source and technical work</h2><p>Selected source repositories and development history are published under the founder’s public GitHub profile. Bounded model and demonstration assets may be published through the MODU Hugging Face organization.</p><p><a href="https://github.com/J2theN1">GitHub profile ↗</a> · <a href="https://huggingface.co/moduindustries">Hugging Face organization ↗</a></p></div></article>
        <article class="evidence-block"><p class="card-number">03</p><div><h2>Working execution surfaces</h2><p>Current development includes local runtime work, PC and phone workers, connected-service bridges, durable browser workflows, and local-model infrastructure. The pitch deck describes the architecture and current stage without representing the system as generally available.</p><p><a href="pitch-deck.html">Technical pitch →</a> · <a href="product.html">Product boundary →</a></p></div></article>
        <article class="evidence-block"><p class="card-number">04</p><div><h2>Security and authority model</h2><p>The public security page documents least authority, secret separation, verifiable receipts, private control paths, data boundaries, responsible disclosure, and the absence of unissued certification claims.</p><p><a href="security.html">Security practices →</a></p></div></article>
        <article class="evidence-block"><p class="card-number">05</p><div><h2>Operating surface</h2><p>The public domain, company mailbox, support route, security-report route, privacy notice, canonical URLs, HTTPS monitoring, and Git-based deployment form a minimal operating surface for review and early conversations.</p><p><a href="support.html">Support →</a> · <a href="privacy.html">Privacy →</a></p></div></article>
        <article class="evidence-block"><p class="card-number">06</p><div><h2>Current limitations</h2><p>MODU is founder-funded active R&amp;D in early validation. This site does not claim recurring revenue, customer adoption, production certification, broad availability, or suitability for regulated use.</p><p><a href="mailto:contact@moduindustries.ca">Request a bounded technical discussion →</a></p></div></article>
    </div>
</section>
"""

COMPANY_BODY = """
<section class="page-hero" aria-labelledby="page-heading"><div class="container"><p class="eyebrow">Company</p><h1 id="page-heading">MODU INDUSTRIES LTD.</h1><p class="hero-lead">Verified company identity and a factual overview of the product work.</p></div></section>
<section class="section"><div class="container prose-wide">
    <h2>Legal identity</h2><p><strong>MODU INDUSTRIES LTD.</strong> is a British Columbia company incorporated on July 25, 2025 under incorporation number <strong>BC1549916</strong>. “Modu Inc.” is an operating brand used by the company.</p><p>Founder and director: <strong>Jason Vetter</strong>. Headquarters: West Kelowna, British Columbia, Canada. Company domain: <a href="https://moduindustries.ca/">moduindustries.ca</a>.</p>
    <h2>What the company is building</h2><p>MODU develops a deterministic, local-first AI and device-orchestration platform for coordinating auditable agents, tools, models, computers, phones, and connected services. The product is in active research and development and early validation.</p>
    <h2>Public evidence</h2><ul class="check-list"><li>Selected source and development history: <a href="https://github.com/J2theN1">GitHub</a>.</li><li>Bounded model and demonstration assets: <a href="https://huggingface.co/moduindustries">Hugging Face</a>.</li><li>Product boundary and architecture: <a href="product.html">Product</a>.</li><li>Evidence index and limitations: <a href="evidence.html">Evidence</a>.</li></ul>
    <h2>Company contacts</h2><p>General: <a href="mailto:contact@moduindustries.ca">contact@moduindustries.ca</a><br>Support: <a href="mailto:contact@moduindustries.ca?subject=Support%20request">contact@moduindustries.ca (Support)</a><br>Security: <a href="mailto:contact@moduindustries.ca?subject=Security%20report">contact@moduindustries.ca (Security)</a></p>
</div></section>
"""

SECURITY_BODY = """
<section class="page-hero" aria-labelledby="page-heading"><div class="container"><p class="eyebrow">Security</p><h1 id="page-heading">Bounded authority and verifiable execution.</h1><p class="hero-lead">Security practices, responsible disclosure, and current assurance status.</p></div></section>
<section class="section"><div class="container prose-wide">
    <h2>Security approach</h2><p>MODU is designed around bounded capabilities, explicit authority, verifiable receipts, and separation between human credentials, machine credentials, private control paths, and public application surfaces.</p><ul class="check-list"><li><strong>Least authority:</strong> integrations receive only the scopes required for their documented job.</li><li><strong>Scoped writes:</strong> reversible sourced work can execute automatically inside a bound workflow; legal, financial, identity, and destructive consequences remain explicit.</li><li><strong>Secret separation:</strong> passwords, tokens, OTPs, recovery codes, and private keys are not intended for public repositories, public logs, or company spreadsheets.</li><li><strong>Verification:</strong> operational work is expected to produce evidence that can be checked rather than relying only on a success message.</li><li><strong>Human gates:</strong> CAPTCHA, MFA, passkeys, legal terms, and payments pause a workflow without inventing or bypassing the missing authority.</li><li><strong>Data boundaries:</strong> personal, health, family, company, and client information are treated as distinct classes.</li></ul>
    <h2>Responsible disclosure</h2><p>Send a good-faith security report to <a href="mailto:contact@moduindustries.ca?subject=Security%20report">contact@moduindustries.ca (Security)</a>. Include the affected service, reproduction steps, impact, and a safe way to contact you. Do not include passwords, private keys, personal data, or unrelated customer information.</p><p>Please do not conduct denial-of-service testing, social engineering, physical intrusion, persistence, data destruction, or testing against third-party systems without written authorization. A public bug-bounty payment is not promised unless agreed in writing before work begins.</p>
    <h2>Current assurance status</h2><p>This page describes working practices and direction. MODU does not claim SOC 2, ISO 27001, HIPAA, government clearance, or another independent certification that has not been formally issued.</p>
</div></section>
"""

SUPPORT_BODY = """
<section class="page-hero" aria-labelledby="page-heading"><div class="container"><p class="eyebrow">Support</p><h1 id="page-heading">A clear route for product, access, and security questions.</h1><p class="hero-lead">What to include, what not to send, and what the current support model covers.</p></div></section>
<section class="section"><div class="container prose-wide">
    <h2>Contact support</h2><p>Email <a href="mailto:contact@moduindustries.ca?subject=Support%20request">contact@moduindustries.ca (Support)</a> for product, access, or account questions. General company enquiries can go to <a href="mailto:contact@moduindustries.ca">contact@moduindustries.ca</a>. Security reports belong at <a href="mailto:contact@moduindustries.ca?subject=Security%20report">contact@moduindustries.ca (Security)</a>.</p>
    <h2>What to include</h2><ul class="check-list"><li>The product, repository, service, or device involved.</li><li>What you expected and what actually happened.</li><li>Relevant timestamps, versions, and non-secret error text.</li><li>Steps already attempted and the business impact.</li></ul><p>Do not send passwords, API keys, OTPs, recovery codes, private keys, unrestricted data exports, or information you are not authorized to disclose.</p>
    <h2>Service expectations</h2><p>Support is currently founder-led and prioritized by severity, contractual commitments, and available evidence. This public page does not create a guaranteed response time or service-level agreement. Any binding support terms must appear in an applicable written contract.</p>
</div></section>
"""

PRIVACY_BODY = """
<section class="page-hero" aria-labelledby="page-heading"><div class="container"><p class="eyebrow">Privacy</p><h1 id="page-heading">A website-scoped privacy notice.</h1><p class="hero-lead">This notice applies to the public site at moduindustries.ca.</p></div></section>
<section class="section"><div class="container prose-wide">
    <h2>Scope</h2><p>This notice applies only to the public website at <a href="https://moduindustries.ca/">moduindustries.ca</a>, not private development systems, client deployments, or separately contracted services.</p>
    <h2>Website data</h2><p>The public website does not provide an account login, payment form, embedded customer database, first-party analytics script, advertising tracker, or third-party font resource. It uses system fonts supplied by the visitor’s device.</p><p>Web hosting, DNS, and content-delivery providers may process ordinary request information such as IP address, browser or user-agent data, requested path, timestamp, and security signals to deliver and protect the site.</p>
    <h2>Email</h2><p>When you email MODU, the company and its email-routing or delivery providers process the address, message, headers, and attachments needed to receive, secure, and respond to the communication. Messages may be retained for business records, security, support, and legal obligations.</p><p>Do not email passwords, OTPs, recovery codes, private keys, or information you are not authorized to disclose.</p>
    <h2>Questions and requests</h2><p>For a question about this notice, email <a href="mailto:contact@moduindustries.ca">contact@moduindustries.ca</a>. Security matters should be sent to <a href="mailto:contact@moduindustries.ca?subject=Security%20report">contact@moduindustries.ca (Security)</a>.</p><p>Last updated: August 3, 2026.</p>
</div></section>
"""

PITCH_BODY = """
<section class="page-hero pitch-hero" aria-labelledby="page-heading"><div class="container"><p class="eyebrow">Startup pitch</p><h1 id="page-heading">Doing more with less.</h1><p class="hero-lead">A local-first, tool-capable runtime for governed and verifiable work across computers, phones, models, and connected services.</p><div class="button-row"><a class="btn btn-primary" href="mailto:contact@moduindustries.ca">Start a conversation</a><a class="btn btn-secondary" href="evidence.html">Review evidence</a></div></div></section>
<section class="section"><div class="container"><div class="section-heading"><p class="eyebrow">Problem</p><h2>Useful AI work still breaks at the execution boundary.</h2></div><div class="card-grid two-up"><article class="card"><h3>Fragmented tools</h3><p>Agents, scripts, connected apps, browsers, and devices behave like separate products instead of one governed execution system.</p></article><article class="card"><h3>Weak verification</h3><p>Assistants can claim success without binding the answer to the actual worker, action, output, and observed result.</p></article><article class="card"><h3>Lost operational context</h3><p>Identity, permissions, procedures, devices, and programme states are repeatedly rediscovered rather than reused as durable infrastructure.</p></article><article class="card"><h3>Cloud-first cost and dependency</h3><p>Metered cloud inference is often the default even when capable local hardware and owner-controlled devices are available.</p></article></div></div></section>
<section class="section section-alt"><div class="container"><div class="section-heading"><p class="eyebrow">Solution</p><h2>One runtime, many bounded workers.</h2></div><div class="card-grid two-up"><article class="card"><h3>Procedural cognition</h3><p>Deterministic procedures, memory, tools, authority, and model reasoning work as separate, inspectable parts of the system.</p></article><article class="card"><h3>Local and heterogeneous compute</h3><p>PC GPUs, CPUs, phones, device accelerators, and selective cloud services can participate in one governed worker fabric.</p></article><article class="card"><h3>Result-bound execution</h3><p>Operations are tied to workers, adapters, action state, outputs, receipts, and the final user-visible result.</p></article><article class="card"><h3>Resumable human gates</h3><p>CAPTCHA, MFA, passkeys, legal terms, and payments pause a workflow without losing its exact state.</p></article></div></div></section>
<section class="section"><div class="container two-column"><div><p class="eyebrow">Current stage</p><h2>Founder-funded active R&amp;D.</h2></div><div class="prose"><p>Working development spans local runtime infrastructure, connected-service bridges, PC and phone workers, persistent browser workflows, local-model orchestration, professional-software automation, and durable evidence systems.</p><p>The company is moving from broad infrastructure toward focused, repeatable pilots. It is early validation, not a claim of general availability, recurring revenue, or production certification.</p></div></div></section>
<section class="section section-alt"><div class="container"><div class="section-heading"><p class="eyebrow">Initial use</p><h2>Start where completion and evidence matter.</h2></div><div class="card-grid two-up"><article class="card"><h3>Developer and IT operations</h3><p>Audits, debugging, deployments, maintenance, connected-service work, and multi-device automation.</p></article><article class="card"><h3>Professional creative pipelines</h3><p>Unreal Engine, Blender, asset preparation, scene inspection, rendering, testing, and verified iteration.</p></article><article class="card"><h3>Evidence-heavy operations</h3><p>Company enrolment, procurement readiness, compliance-oriented procedures, and workflows with human authority gates.</p></article><article class="card"><h3>Small organizations</h3><p>Owner-controlled automation for teams that cannot justify a fragmented stack of metered agents and infrastructure.</p></article></div></div></section>
<section class="section"><div class="container contact-panel"><div><p class="eyebrow">Acceleration</p><h2>Technical review, compute optimization, deployment support, and pilot design.</h2><p>MODU is seeking programs and partners that can help turn working infrastructure into a focused product.</p></div><a class="btn btn-primary" href="mailto:contact@moduindustries.ca">contact@moduindustries.ca</a></div></section>
"""

STYLES = r"""
:root {
    color-scheme: dark;
    --bg: #0b0f14;
    --bg-soft: #101720;
    --panel: #151e29;
    --panel-strong: #1a2633;
    --text: #f2f5f8;
    --muted: #a3afbd;
    --line: #293746;
    --accent: #77d5b5;
    --accent-strong: #a2f1d5;
    --blue: #86bfff;
    --danger: #ffbc90;
    --shadow: 0 22px 70px rgba(0, 0, 0, 0.24);
    --font-sans: Inter, ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
    --font-mono: "SFMono-Regular", Consolas, "Liberation Mono", monospace;
    --content: 1120px;
    --reading: 760px;
}

*, *::before, *::after { box-sizing: border-box; }
html { scroll-behavior: smooth; }
body { margin: 0; background: var(--bg); color: var(--text); font-family: var(--font-sans); font-size: 1rem; line-height: 1.65; }
a { color: var(--accent-strong); text-underline-offset: 0.18em; }
a:hover { color: #fff; }
a:focus-visible, button:focus-visible { outline: 3px solid var(--blue); outline-offset: 3px; }
img { max-width: 100%; }
code { font-family: var(--font-mono); }

.skip-link { position: fixed; left: 1rem; top: -5rem; z-index: 100; background: var(--accent); color: #062019; padding: 0.7rem 1rem; border-radius: 0.5rem; font-weight: 800; }
.skip-link:focus { top: 1rem; }
.container { width: min(calc(100% - 2rem), var(--content)); margin-inline: auto; }
.site-header { position: sticky; top: 0; z-index: 20; border-bottom: 1px solid rgba(41, 55, 70, 0.75); background: rgba(11, 15, 20, 0.92); backdrop-filter: blur(18px); }
.header-inner { min-height: 4.5rem; display: flex; align-items: center; justify-content: space-between; gap: 2rem; }
.logo { display: inline-flex; align-items: center; gap: 0.7rem; color: var(--text); font-weight: 800; text-decoration: none; letter-spacing: -0.02em; white-space: nowrap; }
.logo-mark { display: grid; place-items: center; width: 2rem; height: 2rem; border: 1px solid var(--accent); border-radius: 0.55rem; color: var(--accent); font-family: var(--font-mono); font-size: 0.9rem; }
.nav { display: flex; flex-wrap: wrap; justify-content: flex-end; gap: 0.35rem 1rem; }
.nav a { color: var(--muted); text-decoration: none; font-size: 0.88rem; }
.nav a:hover { color: var(--text); }

.hero, .page-hero { position: relative; overflow: hidden; border-bottom: 1px solid var(--line); background: radial-gradient(circle at 85% 20%, rgba(119, 213, 181, 0.12), transparent 36%), linear-gradient(180deg, #0d131b, var(--bg)); }
.hero { padding: clamp(4.5rem, 9vw, 8.5rem) 0; }
.page-hero { padding: clamp(4rem, 8vw, 7rem) 0; }
.hero-grid { display: grid; grid-template-columns: minmax(0, 1.15fr) minmax(300px, 0.85fr); gap: clamp(2.5rem, 6vw, 6rem); align-items: center; }
.eyebrow { margin: 0 0 0.8rem; color: var(--accent); font-family: var(--font-mono); font-size: 0.78rem; font-weight: 700; letter-spacing: 0.16em; text-transform: uppercase; }
h1, h2, h3 { line-height: 1.12; letter-spacing: -0.035em; }
h1 { max-width: 920px; margin: 0; font-size: clamp(2.55rem, 6vw, 5.8rem); }
.page-hero h1 { max-width: 900px; font-size: clamp(2.45rem, 5vw, 4.8rem); }
h2 { margin: 0; font-size: clamp(2rem, 4vw, 3.5rem); }
h3 { margin: 0 0 0.65rem; font-size: 1.22rem; }
.hero-lead { max-width: 800px; margin: 1.4rem 0 0; color: var(--muted); font-size: clamp(1.08rem, 2vw, 1.35rem); }
.status-line { display: flex; align-items: center; gap: 0.7rem; margin: 1.5rem 0 0; color: var(--muted); font-size: 0.92rem; }
.status-line strong { color: var(--text); }
.status-dot { width: 0.65rem; height: 0.65rem; border-radius: 999px; background: var(--accent); box-shadow: 0 0 0 5px rgba(119, 213, 181, 0.12); }
.status-badge { display: inline-flex; margin-top: 1.5rem; padding: 0.55rem 0.85rem; border: 1px solid rgba(119, 213, 181, 0.35); border-radius: 999px; color: var(--accent-strong); background: rgba(119, 213, 181, 0.08); font-family: var(--font-mono); font-size: 0.78rem; }
.button-row { display: flex; flex-wrap: wrap; gap: 0.8rem; margin-top: 1.75rem; }
.btn { display: inline-flex; align-items: center; justify-content: center; min-height: 2.9rem; padding: 0.7rem 1.1rem; border: 1px solid transparent; border-radius: 0.65rem; text-decoration: none; font-weight: 750; }
.btn-primary { background: var(--accent); color: #062019; }
.btn-primary:hover { background: var(--accent-strong); color: #062019; }
.btn-secondary { border-color: var(--line); background: var(--panel); color: var(--text); }
.btn-secondary:hover { border-color: var(--accent); color: var(--text); }
.hero-panel { padding: 1.5rem; border: 1px solid var(--line); border-radius: 1rem; background: rgba(21, 30, 41, 0.8); box-shadow: var(--shadow); }
.panel-label { margin: 0 0 1rem; color: var(--muted); font-family: var(--font-mono); font-size: 0.75rem; text-transform: uppercase; letter-spacing: 0.14em; }
.flow-list { list-style: none; margin: 0; padding: 0; }
.flow-list li { display: grid; grid-template-columns: 2.25rem 1fr; gap: 0 0.75rem; padding: 0.9rem 0; border-top: 1px solid var(--line); }
.flow-list li:first-child { border-top: 0; padding-top: 0; }
.flow-list span { grid-row: span 2; color: var(--accent); font-family: var(--font-mono); font-size: 0.75rem; }
.flow-list strong { font-size: 0.95rem; }
.flow-list small { color: var(--muted); line-height: 1.45; }

.section { padding: clamp(4rem, 8vw, 7rem) 0; border-bottom: 1px solid var(--line); }
.section-alt { background: var(--bg-soft); }
.section-heading { max-width: 780px; margin-bottom: 2rem; }
.section-heading > p:last-child { color: var(--muted); font-size: 1.08rem; }
.section-link { margin: 1.5rem 0 0; }
.card-grid { display: grid; gap: 1rem; }
.four-up { grid-template-columns: repeat(4, minmax(0, 1fr)); }
.two-up { grid-template-columns: repeat(2, minmax(0, 1fr)); }
.card { padding: 1.45rem; border: 1px solid var(--line); border-radius: 0.9rem; background: linear-gradient(145deg, var(--panel), rgba(21, 30, 41, 0.55)); }
.card p { margin: 0; color: var(--muted); }
.card-number { margin: 0 0 1rem !important; color: var(--accent) !important; font-family: var(--font-mono); font-size: 0.78rem; }
.evidence-list { display: grid; gap: 0.65rem; }
.evidence-item { display: grid; grid-template-columns: 0.65fr 1.5fr auto; gap: 1rem; align-items: center; padding: 1rem 1.1rem; border: 1px solid var(--line); border-radius: 0.75rem; background: var(--panel); text-decoration: none; }
.evidence-item span { color: var(--accent); font-family: var(--font-mono); font-size: 0.74rem; text-transform: uppercase; letter-spacing: 0.1em; }
.evidence-item strong { color: var(--text); font-size: 0.95rem; }
.evidence-item em { color: var(--muted); font-style: normal; font-size: 0.85rem; }
.evidence-item:hover { border-color: var(--accent); }
.architecture-strip { display: grid; grid-template-columns: repeat(4, 1fr); overflow: hidden; border: 1px solid var(--line); border-radius: 0.9rem; }
.architecture-strip div { min-height: 8rem; padding: 1.25rem; border-left: 1px solid var(--line); background: var(--panel); }
.architecture-strip div:first-child { border-left: 0; }
.architecture-strip span { display: block; margin-bottom: 1.5rem; color: var(--accent); font-family: var(--font-mono); font-size: 0.72rem; text-transform: uppercase; letter-spacing: 0.12em; }
.architecture-strip strong { display: block; font-size: 0.94rem; }
.two-column { display: grid; grid-template-columns: 0.8fr 1.2fr; gap: clamp(2rem, 6vw, 6rem); align-items: start; }
.prose { color: var(--muted); font-size: 1.05rem; }
.prose p:first-child { margin-top: 0; }
.contact-panel { display: flex; align-items: center; justify-content: space-between; gap: 2rem; padding: 2rem; border: 1px solid var(--line); border-radius: 1rem; background: var(--panel); }
.contact-panel h2 { max-width: 760px; font-size: clamp(1.8rem, 3vw, 2.8rem); }
.contact-panel p:last-child { color: var(--muted); }
.comparison-grid { display: grid; grid-template-columns: repeat(2, minmax(0, 1fr)); gap: 1rem; }
ul { padding-left: 1.2rem; }
.check-list, .plain-list { margin: 0; color: var(--muted); }
.check-list li, .plain-list li { margin: 0.55rem 0; }
.check-list li::marker { color: var(--accent); }
.tag-grid { display: flex; flex-wrap: wrap; gap: 0.65rem; }
.tag-grid span { padding: 0.55rem 0.75rem; border: 1px solid var(--line); border-radius: 999px; background: var(--panel); color: var(--muted); font-size: 0.86rem; }
.note { margin-top: 1.5rem; padding: 1rem; border-left: 3px solid var(--danger); background: rgba(255, 188, 144, 0.06); color: var(--muted); }
.evidence-sections { display: grid; gap: 1rem; }
.evidence-block { display: grid; grid-template-columns: 3rem 1fr; gap: 1.25rem; padding: 1.5rem; border: 1px solid var(--line); border-radius: 0.9rem; background: var(--panel); }
.evidence-block h2 { font-size: 1.5rem; }
.evidence-block p { color: var(--muted); }
.prose-wide { max-width: var(--reading); }
.prose-wide h2 { margin: 2.7rem 0 0.8rem; font-size: 1.65rem; }
.prose-wide h2:first-child { margin-top: 0; }
.prose-wide p, .prose-wide li { color: var(--muted); }
.pitch-hero { background: radial-gradient(circle at 20% 10%, rgba(134, 191, 255, 0.14), transparent 40%), linear-gradient(180deg, #0d131b, var(--bg)); }

.site-footer { padding: 2.4rem 0; background: #080b0f; }
.footer-inner { display: grid; gap: 0.25rem; }
.footer-inner p { margin: 0; }
.footer-copy { font-weight: 750; }
.footer-legal { color: var(--muted); font-size: 0.82rem; }
.footer-legal a { color: var(--muted); }

@media (max-width: 980px) {
    .header-inner { align-items: flex-start; padding: 1rem 0; }
    .nav { max-width: 580px; }
    .hero-grid, .two-column { grid-template-columns: 1fr; }
    .four-up { grid-template-columns: repeat(2, minmax(0, 1fr)); }
}
@media (max-width: 720px) {
    .header-inner { flex-direction: column; gap: 0.75rem; }
    .nav { justify-content: flex-start; }
    .hero { padding-top: 4rem; }
    .four-up, .two-up, .comparison-grid { grid-template-columns: 1fr; }
    .architecture-strip { grid-template-columns: 1fr 1fr; }
    .architecture-strip div:nth-child(3) { border-left: 0; border-top: 1px solid var(--line); }
    .architecture-strip div:nth-child(4) { border-top: 1px solid var(--line); }
    .evidence-item { grid-template-columns: 1fr; gap: 0.25rem; }
    .contact-panel { align-items: flex-start; flex-direction: column; }
}
@media (max-width: 440px) {
    .container { width: min(calc(100% - 1.25rem), var(--content)); }
    .architecture-strip { grid-template-columns: 1fr; }
    .architecture-strip div { border-left: 0; border-top: 1px solid var(--line); }
    .architecture-strip div:first-child { border-top: 0; }
    .evidence-block { grid-template-columns: 1fr; }
}
"""

DOMAIN_HEALTH = r"""name: Domain health probe

on:
  pull_request:
    paths:
      - "*.html"
      - styles.css
      - robots.txt
      - sitemap.xml
      - CNAME
      - tests/**
      - .github/workflows/domain-health-probe.yml
  push:
    branches: [main]
    paths:
      - "*.html"
      - styles.css
      - robots.txt
      - sitemap.xml
      - CNAME
  workflow_dispatch:
  schedule:
    - cron: "17 15 * * *"

permissions:
  contents: read
  pages: read

jobs:
  contract:
    runs-on: ubuntu-latest
    timeout-minutes: 3
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: "3.12"
      - name: Verify public-site contract
        run: |
          python -m unittest discover -s tests -v
          git diff --check

  probe:
    runs-on: ubuntu-latest
    timeout-minutes: 8
    steps:
      - name: Resolve and probe custom domain
        env:
          GH_TOKEN: ${{ github.token }}
          REPOSITORY: ${{ github.repository }}
          EVENT_NAME: ${{ github.event_name }}
        run: |
          set -uo pipefail
          domain='moduindustries.ca'
          www="www.$domain"
          failed=0
          https_failed=0
          strict_https=1
          if [[ "$EVENT_NAME" == 'pull_request' ]]; then
            strict_https=0
          fi

          echo '=== DNS ==='
          python3 - "$domain" "$www" <<'PY' || failed=1
          import socket
          import sys

          expected_v4 = {
              "185.199.108.153",
              "185.199.109.153",
              "185.199.110.153",
              "185.199.111.153",
          }
          expected_v6 = {
              "2606:50c0:8000::153",
              "2606:50c0:8001::153",
              "2606:50c0:8002::153",
              "2606:50c0:8003::153",
          }
          for host in sys.argv[1:]:
              rows = socket.getaddrinfo(host, 443, type=socket.SOCK_STREAM)
              addresses = {row[4][0] for row in rows}
              print(f"{host}={','.join(sorted(addresses))}")
              if not expected_v4.issubset(addresses) or not expected_v6.issubset(addresses):
                  raise SystemExit(f"unexpected DNS answer set for {host}")
          PY

          echo '=== PAGES API ==='
          pages_json="$({
            curl --fail-with-body --silent --show-error \
              -H 'Accept: application/vnd.github+json' \
              -H "Authorization: Bearer $GH_TOKEN" \
              -H 'X-GitHub-Api-Version: 2022-11-28' \
              "https://api.github.com/repos/$REPOSITORY/pages"
          })" || failed=1
          printf '%s\n' "$pages_json" \
            | python3 -c 'import json,sys; p=json.load(sys.stdin); print(json.dumps({k:p.get(k) for k in ("status","html_url","cname","https_enforced","protected_domain_state","pending_domain_unverified_at","https_certificate")},sort_keys=True))' \
            || failed=1
          PAGES_JSON="$pages_json" python3 - "$domain" <<'PY' || failed=1
          import json
          import os
          import sys

          expected = sys.argv[1]
          payload = json.loads(os.environ["PAGES_JSON"])
          if payload.get("status") != "built":
              raise SystemExit("Pages is not built")
          if payload.get("cname") != expected:
              raise SystemExit("Pages custom domain mismatch")
          PY

          echo '=== HTTP ==='
          http_result="$(curl --silent --show-error --location --head \
            --connect-timeout 10 --max-time 30 \
            --write-out 'RESULT http_code=%{http_code} final=%{url_effective} verify=%{ssl_verify_result}\n' \
            "http://$domain/")" || failed=1
          printf '%s\n' "$http_result"
          grep -q 'RESULT http_code=200' <<<"$http_result" || failed=1

          echo '=== HTTPS APEX ==='
          apex_result="$(curl --silent --show-error --location --head \
            --connect-timeout 10 --max-time 30 \
            --write-out 'RESULT http_code=%{http_code} final=%{url_effective} verify=%{ssl_verify_result}\n' \
            "https://$domain/")" || https_failed=1
          printf '%s\n' "$apex_result"
          grep -q 'RESULT http_code=200' <<<"$apex_result" || https_failed=1
          grep -q 'verify=0' <<<"$apex_result" || https_failed=1

          echo '=== HTTPS WWW ==='
          www_result="$(curl --silent --show-error --location --head \
            --connect-timeout 10 --max-time 30 \
            --write-out 'RESULT http_code=%{http_code} final=%{url_effective} verify=%{ssl_verify_result}\n' \
            "https://$www/")" || https_failed=1
          printf '%s\n' "$www_result"
          grep -q 'RESULT http_code=200' <<<"$www_result" || https_failed=1
          grep -q 'verify=0' <<<"$www_result" || https_failed=1

          echo '=== TLS CERTIFICATE ==='
          certificate="$(timeout 20 openssl s_client -connect "$domain:443" -servername "$domain" </dev/null 2>/dev/null \
            | openssl x509 -noout -subject -issuer -dates -ext subjectAltName)" || https_failed=1
          printf '%s\n' "$certificate"
          grep -q "DNS:$domain" <<<"$certificate" || https_failed=1
          grep -q "DNS:$www" <<<"$certificate" || https_failed=1

          if [[ "$EVENT_NAME" != 'pull_request' ]]; then
            echo '=== PUBLIC PATHS ==='
            paths=(/ /product.html /evidence.html /company.html /security.html /support.html /privacy.html /pitch-deck.html /robots.txt /sitemap.xml)
            for path in "${paths[@]}"; do
              ok=0
              for attempt in {1..12}; do
                body="$(mktemp)"
                code="$(curl --silent --show-error --location --connect-timeout 10 --max-time 30 --output "$body" --write-out '%{http_code}' "https://$domain$path")" || code=000
                if [[ "$code" == '200' ]] && ! grep -Fq "There isn't a GitHub Pages site here" "$body"; then
                  echo "$path=200"
                  ok=1
                  rm -f "$body"
                  break
                fi
                rm -f "$body"
                sleep 10
              done
              [[ "$ok" -eq 1 ]] || failed=1
            done
          fi

          if [[ "$https_failed" -ne 0 ]]; then
            if [[ "$strict_https" -eq 1 ]]; then
              failed=1
            else
              echo 'HTTPS_PROVISIONING=PENDING'
            fi
          fi

          if [[ "$failed" -ne 0 ]]; then
            echo 'DOMAIN_HEALTH=FAIL'
            exit 1
          fi
          echo 'DOMAIN_HEALTH=PASS'
"""

ROBOTS = """User-agent: *
Allow: /

Sitemap: https://moduindustries.ca/sitemap.xml
"""

SITEMAP = """<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
  <url><loc>https://moduindustries.ca/</loc></url>
  <url><loc>https://moduindustries.ca/product.html</loc></url>
  <url><loc>https://moduindustries.ca/evidence.html</loc></url>
  <url><loc>https://moduindustries.ca/company.html</loc></url>
  <url><loc>https://moduindustries.ca/security.html</loc></url>
  <url><loc>https://moduindustries.ca/support.html</loc></url>
  <url><loc>https://moduindustries.ca/privacy.html</loc></url>
  <url><loc>https://moduindustries.ca/pitch-deck.html</loc></url>
</urlset>
"""

PAGES = {
    "index.html": render_page(
        path="index.html",
        title="Modu Inc. — Local-first AI and device orchestration",
        description="MODU is building a local-first AI and device-orchestration platform for governed, auditable work across computers, phones, models, and connected services.",
        body=HOME_BODY,
        extra_head=HOME_STRUCTURED_DATA,
    ),
    "product.html": render_page(
        path="product.html",
        title="Product — Modu Inc.",
        description="The current product boundary and architecture of MODU, a local-first platform for governed AI, tools, devices, and verifiable execution.",
        body=PRODUCT_BODY,
    ),
    "evidence.html": render_page(
        path="evidence.html",
        title="Evidence — Modu Inc.",
        description="A bounded public index of MODU company identity, source, technical work, security practices, operating surface, and current limitations.",
        body=EVIDENCE_BODY,
    ),
    "company.html": render_page(
        path="company.html",
        title="Company — MODU INDUSTRIES LTD.",
        description="Verified company identity and a factual overview of MODU INDUSTRIES LTD. and its current local-first AI product work.",
        body=COMPANY_BODY,
    ),
    "security.html": render_page(
        path="security.html",
        title="Security — MODU INDUSTRIES LTD.",
        description="MODU security practices covering bounded authority, scoped writes, secret separation, verification, human gates, and responsible disclosure.",
        body=SECURITY_BODY,
    ),
    "support.html": render_page(
        path="support.html",
        title="Support — MODU INDUSTRIES LTD.",
        description="How to request MODU product or account support, what evidence to include, and what sensitive information should never be emailed.",
        body=SUPPORT_BODY,
    ),
    "privacy.html": render_page(
        path="privacy.html",
        title="Privacy — MODU INDUSTRIES LTD.",
        description="A website-scoped privacy notice for moduindustries.ca, including hosting request data, email handling, and the absence of trackers and third-party fonts.",
        body=PRIVACY_BODY,
    ),
    "pitch-deck.html": render_page(
        path="pitch-deck.html",
        title="Startup Pitch — MODU INDUSTRIES LTD.",
        description="MODU startup pitch: local-first AI, procedural cognition, cross-device workers, result-bound execution, current stage, and acceleration needs.",
        body=PITCH_BODY,
    ),
}

for relative, content in PAGES.items():
    (ROOT / relative).write_text(content, encoding="utf-8")

(ROOT / "styles.css").write_text(dedent(STYLES).lstrip(), encoding="utf-8")
(ROOT / "robots.txt").write_text(ROBOTS, encoding="utf-8")
(ROOT / "sitemap.xml").write_text(SITEMAP, encoding="utf-8")
(ROOT / ".github/workflows/domain-health-probe.yml").write_text(
    dedent(DOMAIN_HEALTH).lstrip(), encoding="utf-8"
)
