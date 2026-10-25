# 13 — Canadian Content Worksheet + Price-Certification Basis (2026-10-15)

**Purpose:** close finding **H1** (and support **H4**) in `12-compliance-redteam-20261015.md`. The draft's supporting statement claims an "actual figure" of **100%** Canadian content. That figure is not provable today: the subcontracted roles are unnamed, and no licence, dataset, or rental line identifies a supplier or its origin. This worksheet replaces the 100% gloss with a line-item calculation MODU can sign honestly, and lists every origin check that has to close before the certification is filed **with** the proposal.

**The rule (CFP 006, Amendment 2, W7714-248676):**
- §7.10.3: the offeror "certifies that a minimum of 70 percent (70%) of the total bid price consists of Canadian goods and Canadian services as defined in section 'c' of clause 3.130, as amended herein"; the certification must be **completed with the bid** — failure to provide it means the goods/services are treated as non-Canadian.
- §1.5 / §7.10.3: SACC Manual clause **A3050T (2020-07-01)** is amended — "Eighty percent" deleted, "**Seventy percent**" inserted. For a mix of goods and services, §7.10.3 points to **Annex 3.6 of the Supply Manual** for the content calculation.
- §4.1.3: Canada "may conduct the validation of Canadian Content certifications **at any time** in the evaluation process."
- Part 5 preamble: a certification "found to be untrue, whether made knowingly or unknowingly" can render the proposal non-responsive or the contractor in default.
- The test is **origin** (where the good is produced / who supplies the service and where it is performed), **not** where the item is consumed. The draft's "consumed at MODU's West Kelowna laboratory" reasoning does not satisfy it.
- Sourcing note: the CFP incorporates the A3050T / clause 3.130(c) definition and the Annex 3.6 method by reference; it does not reproduce their full text. This worksheet applies the origin principle as stated in the CFP and the red-team read; the final arithmetic follows Annex 3.6 at the Oct 22 financial build.

**Worksheet conventions (deliberately conservative):**
- **Proven** = the Canadian origin is established by facts already on record in this pack (not by intention, role description, or likelihood).
- Any line not proven is **counted as non-Canadian** in the percentage until its check closes — the H1 fix: "uncertain items counted as non-Canadian and the threshold re-proven on the remainder."
- Amounts are taken from `05-proposal-draft-v1.md` PRC-7 exactly as built. Where the proposal does not split a line or name a supplier, that is marked, not filled in.

---

## 1. Line-item worksheet

Total bid price: **$1,075,000** (labour $1,002,000 + non-labour $73,000 + travel $0). 70% threshold = **$752,500**.

| # | Line (from `05` PRC-7) | Amount (CAD) | Canadian-content basis claimed | Evidence that proves it | Status |
|---|---|---|---|---|---|
| L1 | Principal Investigator / Chief Architect — MODU (J. Vetter), 1,760 h × $150 | $264,000 | Canadian service: MODU's own labour, performed in Canada | On record in the pack: MODU INDUSTRIES LTD. incorporated in BC (BC1549916); sole director and 100% owner resident in Canada; work performed at MODU's West Kelowna, BC laboratory (`05` Field 0 + Certifications; company facts) | **proven** |
| L2 | Military Messaging Standards Specialist (subcontract), 940 h × $140 | $131,600 | Draft claims the role is Canada-based | None on file — the role is **unnamed**; no firm or person is selected, so no origin can be evidenced | **must-decide** (select, then verify) |
| L3 | Software Engineer — Fusion & Standards (subcontract), 2,220 h × $140 | $310,800 | Draft claims the role is Canada-based | None on file — role unnamed. **Largest subcontract line; threshold-critical (see §2)** | **must-decide** (select, then verify) |
| L4 | RF Systems Engineer (subcontract, part-time), 1,060 h × $130 | $137,800 | Draft claims the role is Canada-based | None on file — role unnamed | **must-decide** (select, then verify) |
| L5 | Software Engineer — Integration Prototype (subcontract), 620 h × $130 | $80,600 | Draft claims the role is Canada-based | None on file — role unnamed | **must-decide** (select, then verify) |
| L6 | CAF Operational Advisor (subcontract), 128 h × $125 | $16,000 | Draft claims the role is Canada-based | None on file — individual unnamed. PRC-4 describes a *former* signals/C2 operator; a Canada-resident individual would make this a Canadian service, but that is a selection fact, not a record fact | **must-decide** (select, then verify) |
| L7 | Technical Documentation (contract), 816 h × $75 | $61,200 | Draft claims the role is Canada-based | None on file — contractor unnamed | **must-decide** (select, then verify) |
| N1 | M1 — published standards reference sets + NIEM/MTF mapping tooling licences | $11,000 | Draft claims licences/datasets sourced in Canada | None on file — no product or supplier named; the split between reference sets and tooling is **[FROM PROPOSAL — verify]** | **checkable-now** (once products are named: supplier invoice + vendor origin) |
| N2 | M2 — bearer-simulation kit rentals + recorded-traffic datasets | $24,000 | Draft claims rentals/datasets sourced in Canada | None on file — rental supplier and dataset licensor both **[UNKNOWN]** | **checkable-now** (supplier/licensor confirmation) |
| N3 | M3 — fusion test tooling + data licences | $8,000 | Draft claims licences sourced in Canada | None on file — vendors **[UNKNOWN]** | **checkable-now** (vendor origin from licence/invoice) |
| N4 | M4 — conformance/schema-validation tooling licences + test harnesses | $17,000 | Draft claims licences sourced in Canada | None on file — vendors **[UNKNOWN]**; schema-tooling vendors are frequently non-Canadian, so this line must not be assumed | **checkable-now** (vendor origin from licence/invoice) |
| N5 | M5 — demonstration-environment rentals (bearer emulation, hosting) | $13,000 | Draft claims rentals sourced in Canada | None on file — rental supplier and hosting provider **[UNKNOWN]**; for hosting, the test is the provider's origin, not the server's region | **checkable-now** (supplier/provider origin) |
| T1 | Travel (all milestones) | $0 | n/a — no travel is priced | `05` PRC-7: all work at the West Kelowna laboratory; $0 in every milestone | proven (no content effect) |

**Worksheet line count: 13** (7 labour + 5 non-labour + 1 zero-travel line).

---

## 2. The honest percentage — proven basis, and what it becomes as checks close

**Proven today: $264,000 ÷ $1,075,000 = 24.6%.** Only line L1 (MODU's own labour) is proven. Every other line is counted as non-Canadian until its check closes. On today's evidence MODU **cannot yet sign** the 70% certification — which is exactly why the checks in §3 exist, and why they are selection-and-paperwork tasks, not design work.

| Scenario (cumulative, conservative — unchecked lines counted non-Canadian) | Canadian $ | % of $1,075,000 | ≥ 70% ($752,500)? |
|---|---|---|---|
| Proven today (L1 only) | $264,000 | 24.6% | ✗ — shortfall $488,500 |
| All labour verified Canadian (L1–L7); all non-labour counted non-Canadian | $1,002,000 | **93.2%** | ✓ — headroom $249,500 |
| All labour + all non-labour verified | $1,075,000 | 100% | ✓ — claimable **only** in this state, never before |

**Sensitivity — why verification order matters (verify largest lines first):**

| If this line fails its origin check… | Canadian $ (labour-verified basis) | % | Result |
|---|---|---|---|
| L3 Fusion & Standards Engineer ($310,800) is non-Canadian | $691,200 | 64.3% | ✗ — **below threshold by $61,300** |
| L2 + L4 ($131,600 + $137,800) are non-Canadian | $732,600 | 68.1% | ✗ — below threshold by $19,900 |
| L5 + L6 + L7 ($80,600 + $16,000 + $61,200) are non-Canadian | $844,200 | 78.5% | ✓ |
| All non-labour (N1–N5, $73,000) is non-Canadian | $1,002,000 | 93.2% | ✓ |

**Reading:** the threshold does not depend on the non-labour lines at all — it stands or falls on the subcontracted labour, and above all on L3. If L3 cannot be placed with a Canadian supplier, the bid must be restructured (re-scope the line to MODU labour or a Canadian firm) **before** submission, not explained after. The defensible figure for the v2 supporting statement is whatever this worksheet computes on the day the checks close — expected landing zone 93.2% (labour-verified, non-labour conservatively excluded), stated as such, in place of "100%".

**Verification priority order (by dollars at risk):** L3 ($310,800) → L4 ($137,800) → L2 ($131,600) → L5 ($80,600) → L7 ($61,200) → L6 ($16,000) → N2 ($24,000) → N4 ($17,000) → N5 ($13,000) → N1 ($11,000) → N3 ($8,000).

---

## 3. Origin checks list — 16 checks

Each check closes when the named evidence is on file in the pack. "Supplier confirmation" means a written statement from the supplier (email is sufficient at this stage) or an invoice/licence naming the supplier, plus the supplier's Canadian basis (incorporation or residence, and where the work is performed).

**Subcontracted roles — select the firm/person first, then verify (6 checks):**
1. **L2 Standards Specialist** — select firm/person; written confirmation they are Canadian (incorporated or resident in Canada) and the work is performed in Canada.
2. **L3 Fusion & Standards Engineer** — same. **Threshold-critical:** close this check first; if it cannot close Canadian, escalate to Jason for re-scoping before any other check matters.
3. **L4 RF Systems Engineer** — same confirmation.
4. **L5 Integration Prototype Engineer** — same confirmation.
5. **L6 CAF Operational Advisor** — confirm the individual is resident in Canada. (Selection also feeds red-team H2: former vs **current** public servant status under §5.2.6 / §3.1.1 — record the answer when the person is selected.)
6. **L7 Technical Documentation contractor** — same confirmation.

**Non-labour — verify from the transaction documents (10 checks):**
7. **N1a Standards reference sets** — identify the actual sets to be bought; supplier invoice + supplier origin.
8. **N1b Mapping tooling licences** — identify the actual tooling; licence/invoice naming the vendor + vendor origin (vendor's terms/about page as secondary evidence).
9. **N2a Bearer-simulation kit rentals** — rental agreement/invoice naming the supplier + supplier origin.
10. **N2b Recorded-traffic datasets** — licensor named on the licence + licensor origin.
11. **N3a Fusion test tooling licences** — vendor named on the licence/invoice + vendor origin.
12. **N3b Data licences** — licensor named + licensor origin.
13. **N4a Conformance/schema-validation tooling licences** — vendor named + vendor origin. Do not assume: this category is frequently foreign-supplied; if a chosen tool is non-Canadian, the line is simply counted non-Canadian (the threshold does not need it — see §2).
14. **N4b Test harnesses** — confirm whether harnesses are rented/bought (supplier + origin) or built by MODU labour (then the value already sits in the labour lines and must not be double-counted here — **[FROM PROPOSAL — verify]** at the Oct 22 build).
15. **N5a Bearer-emulation rentals** — rental supplier named + origin.
16. **N5b Demonstration hosting** — hosting provider named + provider origin (incorporation/residence of the provider, not data-centre region).

**Checks count: 16** (6 labour + 10 non-labour).

---

## 4. H4 addendum — cost basis the founder-labour line needs before the price certification can be signed

The §5.2.10 certification (first branch) reads: the price "is based on costs computed in accordance with **Contract Cost Principles 1031-2**, and includes an estimated amount of profit of CAD _________. The total amount of profit must not exceed **fifteen percent (15%) of the total bid price**." For this bid: profit cap = 15% × $1,075,000 = **$161,250**. The draft's rates are currently "planning rates," substantiation is deferred to negotiation, no profit figure exists, and the largest line — the founder's own 1,760 h / $264,000 (L1) — has no payroll or engagement record behind it (pack record: MODU has no employees and no payroll history today). Checklist for the **Oct 22 financial build** — all items close **before submission**, not at negotiation:

- [ ] **Decide the PI's engagement basis for the contract** — employee salary vs director's fee vs subcontract. Each carries a different 1031-2 cost treatment; the rate build cannot start until this is decided. (Jason decision, with accountant.)
- [ ] **Create the engagement record that matches the decision** — employment agreement + payroll setup (CRA payroll account, source deductions) if salary; written services agreement if director's fee/subcontract. The document must exist before the certification is signed; today none exists.
- [ ] **Build rate substantiation for every labour category under 1031-2** — direct cost per category plus the overhead treatment the Principles allow; subcontract categories (L2–L7) supported by the selected firms' quotes/rate cards (same selections as §3 — one task closes both H1 and H4).
- [ ] **Compute the embedded profit explicitly and fill the §5.2.10 blank** — total price − total costed cost = profit; show the arithmetic; confirm profit ≤ $161,250 (15% of $1,075,000). Profit distributed invisibly inside "planning rates" is not a figure MODU can certify.
- [ ] **Select the §5.2.10 certification branch** (the 1031-2 branch is the expected one for MODU) and **portal-check** whether the certification is a financial-bid form field for this challenge (carried from H4's fix list; §3.8.1 leaves the required-with-proposal set to the live form).
- [ ] **Strike "planning rates" from all submitted text** — PRC-7's "price support … will be available at negotiation" becomes a statement of the substantiation that exists at submission.
- [ ] **Evidence discipline for L1 from contract day one** — contemporaneous timesheets for the PI's 1,760 h and project cost records kept audit-clean (the draft already commits to the 6-year audit window; the founder line is the one an auditor will test first, and it is also the worksheet's only proven content line — its records carry both certifications).
- [ ] **Accountant review of the completed rate build before submission** (red-team H4 fix: "with accountant, before submission — not at negotiation"), sized against the two-month negotiation clock in §4.5.4.

---

## 5. What v2's supporting statement should say

Replace the "actual figure is 100%" paragraph with: the certification of the 70% threshold, the worksheet figure **as computed when the §3 checks close** (expected: 93.2% on verified Canadian labour alone, with non-labour conservatively excluded unless individually verified), and one sentence naming this worksheet as the basis. If any check is still open at submission, its line stays counted as non-Canadian and the stated figure is the lower, true one.

*Prepared 2026-10-15, prep only — `05` was not edited. Sources: `12-compliance-redteam-20261015.md` (H1, H4), `05-proposal-draft-v1.md` PRC-7 (all amounts, hours, rates, and non-labour itemizations), CFP 006 Amendment 2 text in `sources/cfp006.txt` (§§1.5, 4.1.3, 5.2.10, 7.10.3) and `01-solicitation-guide.md`. No figures were invented: every amount traces to the proposal's own tables; splits and suppliers the proposal does not name are marked [FROM PROPOSAL — verify] or [UNKNOWN].*
