# Public Product Evidence Site Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Turn the existing MODU corporate website into a concise, factual public product-evidence site suitable for startup-program review while preserving the current GitHub Pages and Cloudflare DNS architecture.

**Architecture:** Keep the site static and dependency-free in `J2theN1/modu-inc-website`, published from `main` through GitHub Pages at `moduindustries.ca`. Separate the public narrative into a focused homepage, a product page, and an evidence page; retain the existing company, security, support, privacy, and pitch-deck pages. Add automated content/link/privacy checks so unsupported claims and broken public paths cannot silently return.

**Tech Stack:** HTML5, CSS3, Python 3 standard library tests, GitHub Pages, GitHub Actions, Cloudflare DNS/Registrar.

## Global Constraints

- Preserve `CNAME` with the exact value `moduindustries.ca`.
- Do not introduce a framework, package manager, analytics script, advertising tracker, cookie banner, backend, login, payment form, or public home-network ingress.
- Do not claim production availability, customer adoption, revenue, certifications, model superiority, or functionality that lacks current public evidence.
- Use `MODU INDUSTRIES LTD.` as the legal entity and `Modu Inc.` only as the operating brand.
- Use `contact@moduindustries.ca` for public contact, support, and security routing.
- Keep GitHub Pages as the public host and Cloudflare as registrar/DNS; do not migrate the primary site to a Worker or home server.
- Remove third-party font requests and use local system font stacks.
- Every public HTML page must include a unique title, description, canonical URL, accessible navigation, and links to Company, Security, Support, and Privacy.

---

### Task 1: Add the public-site contract tests

**Files:**
- Create: `tests/test_public_site.py`

**Interfaces:**
- Consumes: public files in the repository root.
- Produces: `python -m unittest discover -s tests -v` as the canonical site verification command.

- [ ] **Step 1: Write failing tests**

Create standard-library tests that require:

```python
REQUIRED_PAGES = {
    "index.html",
    "product.html",
    "evidence.html",
    "company.html",
    "security.html",
    "support.html",
    "privacy.html",
    "pitch-deck.html",
}
```

The tests must parse local links, require unique metadata and canonical URLs, reject Google Fonts/analytics/tracker references, reject the phrases `as capable as the big names`, `90+ API routes`, and `100+ commands` from the homepage, validate `robots.txt` and `sitemap.xml`, and assert that every local link target exists.

- [ ] **Step 2: Run tests to verify RED**

Run:

```bash
python -m unittest discover -s tests -v
```

Expected: failures for missing `product.html`, `evidence.html`, `robots.txt`, `sitemap.xml`, third-party font references, and unsupported homepage claims.

- [ ] **Step 3: Commit the RED test**

```bash
git add tests/test_public_site.py
git commit -m "test: define public product evidence contract"
```

### Task 2: Publish the focused homepage and product page

**Files:**
- Modify: `index.html`
- Create: `product.html`
- Modify: `styles.css`

**Interfaces:**
- Consumes: verified company identity, existing product narrative, public GitHub and Hugging Face organization links.
- Produces: a concise startup-review landing page and a detailed factual product page.

- [ ] **Step 1: Replace the homepage narrative**

The homepage must state:

```text
MODU is a local-first AI and device-orchestration platform for auditable work across computers, phones, models, and connected services.
```

Include four sections: Product, Working Evidence, Architecture, and Current Stage. Link to `product.html`, `evidence.html`, `pitch-deck.html`, the public GitHub profile, Company, Security, Support, Privacy, and contact email. Remove the healthcare/government vision claims, command-count metrics, and comparative-superiority language from the homepage.

- [ ] **Step 2: Add the product page**

Describe the current product boundary through four components:

```text
Governed workflows
Local and heterogeneous compute
Cross-device execution
Result-bound verification
```

Clearly label the product as active R&D / early validation, distinguish existing infrastructure from planned capabilities, and include no download or general-availability claim.

- [ ] **Step 3: Update shared styles**

Use system font stacks only. Add reusable styles for status badges, evidence cards, architecture steps, compact page navigation, and responsive grids. Keep focus-visible and skip-link support.

- [ ] **Step 4: Run focused tests**

```bash
python -m unittest tests.test_public_site.PublicSiteContractTests.test_required_pages_exist -v
python -m unittest tests.test_public_site.PublicSiteContractTests.test_homepage_avoids_unsupported_claims -v
```

Expected: PASS.

- [ ] **Step 5: Commit**

```bash
git add index.html product.html styles.css
git commit -m "site: publish focused MODU product narrative"
```

### Task 3: Publish the evidence page and normalize trust pages

**Files:**
- Create: `evidence.html`
- Modify: `company.html`
- Modify: `security.html`
- Modify: `support.html`
- Modify: `privacy.html`
- Modify: `pitch-deck.html`

**Interfaces:**
- Consumes: public repository URLs, company incorporation facts, public-domain contact paths, and current assurance disclaimers.
- Produces: a durable evidence index and consistent navigation/privacy behavior across all public pages.

- [ ] **Step 1: Add the evidence page**

Publish bounded evidence categories:

```text
Company identity
Public source and technical work
Working execution surfaces
Security and authority model
Current stage and limitations
```

Link only to public resources. Do not expose private repository names, device addresses, account identifiers, secret paths, or internal queue locations.

- [ ] **Step 2: Normalize every trust page**

Remove Google Fonts tags, add Product and Evidence navigation, add Open Graph metadata, and preserve existing factual disclaimers. Update Privacy to state that the site uses system fonts and intentionally loads no third-party font resource.

- [ ] **Step 3: Normalize the pitch deck**

Add Product, Evidence, Company, and Contact navigation; remove unsupported numeric inventory claims unless they are linked to a current public evidence source; keep the founder-funded / early-validation stage explicit.

- [ ] **Step 4: Run metadata, privacy, and link tests**

```bash
python -m unittest tests.test_public_site.PublicSiteContractTests.test_metadata_and_navigation -v
python -m unittest tests.test_public_site.PublicSiteContractTests.test_no_third_party_fonts_or_trackers -v
python -m unittest tests.test_public_site.PublicSiteContractTests.test_local_links_resolve -v
```

Expected: PASS.

- [ ] **Step 5: Commit**

```bash
git add evidence.html company.html security.html support.html privacy.html pitch-deck.html
git commit -m "site: add public evidence and normalize trust pages"
```

### Task 4: Add discoverability and release verification

**Files:**
- Create: `robots.txt`
- Create: `sitemap.xml`
- Modify: `.github/workflows/domain-health-probe.yml`

**Interfaces:**
- Consumes: the canonical public page set.
- Produces: search-engine discovery metadata and a release probe that checks the new public product/evidence paths.

- [ ] **Step 1: Add robots and sitemap files**

`robots.txt` must allow crawling and reference `https://moduindustries.ca/sitemap.xml`. `sitemap.xml` must include all eight canonical public pages using absolute HTTPS URLs.

- [ ] **Step 2: Extend the domain health probe**

After the apex HTTPS check, probe `/product.html`, `/evidence.html`, `/company.html`, `/security.html`, `/support.html`, `/privacy.html`, `/pitch-deck.html`, `/robots.txt`, and `/sitemap.xml`. Require HTTP 200 and reject responses containing GitHub Pages’ `There isn't a GitHub Pages site here` marker.

- [ ] **Step 3: Run the complete local gate**

```bash
python -m unittest discover -s tests -v
git diff --check
```

Expected: all tests PASS and no whitespace errors.

- [ ] **Step 4: Commit**

```bash
git add robots.txt sitemap.xml .github/workflows/domain-health-probe.yml
git commit -m "site: add discovery and release probes"
```

### Task 5: Review, merge, and verify the public deployment

**Files:**
- Review all changed files.

**Interfaces:**
- Consumes: Tasks 1–4.
- Produces: one reviewed pull request, a merged GitHub Pages deployment, and recorded public-site evidence.

- [ ] **Step 1: Review exact scope**

```bash
git diff --stat main...HEAD
git diff --check main...HEAD
python -m unittest discover -s tests -v
```

Confirm no CNAME, domain architecture, email destination, or private identifier changed.

- [ ] **Step 2: Open the pull request**

The PR description must list the factual-claim reductions, new Product/Evidence pages, privacy improvement, test count, and deployment checks.

- [ ] **Step 3: Merge only the verified head**

Use the exact expected head SHA when merging.

- [ ] **Step 4: Verify public deployment**

Require GitHub Pages build success, domain health probe success, HTTP 200 for every sitemap page, correct canonical URLs, and no third-party font requests in published HTML.

- [ ] **Step 5: Update the business-access registry**

Record the public product site and evidence page as verified dependencies for Cloudflare for Startups, Microsoft for Startups, AWS Activate, NVIDIA Inception, Intel Liftoff, Google for Startups, and DigitalOcean Hatch.
