# 18 — Scenario B Rebuild: the worked example's arithmetic, redone with every assumption stated (2026-10-16)

**What this is:** the rebuild of pre-draft `09` §7 Scenario B required by file `17`'s must-fix #2 (finding **C2**). It recomputes the scenario from stated assumptions, line by line, and gives the verdict: what the corrected numbers are, and the smallest change that makes the scenario a *true* demonstration of the prioritization claim.
**Status:** `09` is **not edited**. Oct 21 adopts this rebuild — or the fallback wording in §7 — by decision, the same way the rehearsal's corrections wait for the Oct 22 build.
**Evidence limits (inherited from `09`, unchanged):** no MODU HF or STANAG 5066 measurement exists and none is claimed. Every bearer parameter below is the annex's public-record figure (`07` §1.5, verified at `17` B1). Message sizes are illustrative assumptions — the difference from `09` is that here they are all stated, sized, and auditable.

---

## 1. What was wrong (file `17`, finding C2, in brief)

`09` §7 claims Scenario B's policy spend is "≈ a third of the raw window" against "≈2.5 windows under naive whole-form FIFO." On the scenario's own stated inputs both numbers fail:

- The whole-form queue totals 23 KB ≈ **153 s ≈ 0.26 of the 10-minute window** at the typical rate — naive FIFO fits inside one window, not 2.5. Reaching 2.5 windows would need ≈230 KB of queue, or a ≈120 bit/s bearer.
- The policy side (order ≈13 s + four deltas ≈2–3 s each + two summaries of unstated size) sums to ≈21–25 s plus unsized summaries. Reaching ≈200 s (a third of the window) needs ≈175 s of turnaround/ARQ or summary bulk that the scenario expressly excludes ("before turnaround/ARQ") and never sizes.

**One further check this rebuild adds:** the two original numbers are not jointly satisfiable at *any* bearer rate for this queue. FIFO cost and policy cost are both dominated by the same data bytes (ratio ≈6:1 by volume), so no single rate makes FIFO = 1,500 s and policy = 200 s at once — at least one of the pair had to be wrong; in fact both were. The scenario's *direction* (form choice saves the window) survives; its headlines do not.

---

## 2. Assumptions — all of them, stated

| # | Assumption | Value | Source / basis |
|---|---|---|---|
| A1 | Bearer | HF, STANAG 5066, simplex | `09` §§2.2, 6; `07` §1.5 |
| A2 | Contact window | One predicted window, **600 s** (10 min) | `09` §7, as given |
| A3 | Bearer rates | Case A: **1,200 bit/s** (the annex's *typical* figure). Case B: **300 bit/s** (a poor-conditions point inside the same envelope) | Envelope 75–9,600 bit/s, typical ≈1,200: `07` §1.5 / `09` §2.2 (`17` B1 VERIFIED) |
| A4 | Units | Decimal: 1 KB = 1,000 B; bit/s ÷ 8 = B/s. Raw rates: 1,200 bit/s = 150 B/s; 300 bit/s = 37.5 B/s; window raw capacity 90,000 B / 22,500 B | Pack convention (`17` C1) |
| A5 | ARQ / retransmission | Effective data rate = **0.8 × raw** (one retransmission per five transmissions, in expectation). Case A effective: 120 B/s. Case B effective: 30 B/s | `09` §2.2's "derated by observed success," given a number. **Assumption, not a measurement** |
| A6 | Turnaround | **5 s per discrete transmission**, charged per message sent, on top of data time | Inside the public record's "seconds to tens of seconds" (`09` §2.2). Midpoint-low; sensitivity at 10 s in §6. **Assumption, not a measurement** |
| A7 | Message sizes — whole | Order **2,000 B**; situation report **3,000 B**; logistics message **1,500 B** | `09` §7, as given |
| A8 | Message sizes — reduced | Report **delta 375 B**; logistics **summary 400 B** | Delta: `09`'s "a few hundred bytes (≈2–3 s each)" at 150 B/s = 300–450 B; midpoint taken. Summary: **this rebuild's assumption** — `09` never sized summaries (`17` C2); 400 B carries §3.3's field set (identity, state essentials, timestamp, provenance pointer) at ≈27% of whole |
| A9 | Queue at window open | **12 objects**: 1 order; **5 report objects** — 4 current situation reports (different originators) + 1 earlier report superseded by a newer one from the same originator; 6 routine logistics messages | `09` §7 lists the four reports and then mentions the pruned "queued earlier report" separately; this rebuild counts it in the queue, where `17`'s 23 KB figure did not — the difference is disclosed, and it favours the original's contrast, not this rebuild's |
| A10 | Policy behaviour | Order crosses whole (§3.4 draft hard core — orders never reduce). The 4 current reports cross as deltas vs last-acknowledged state. 2 near-deadline logistics cross as summaries; 4 defer with aging. The superseded report is pruned: 0 s, 0 transmissions | `09` §7 as written; §3.4 (D-B2 draft position) |
| A11 | FIFO baseline | Every queued object, whole form, in arrival order — including the superseded report (a naive queue does not know). Arrival order assumed = accumulation order: logistics batch first, then the reports (stale first), then the order, issued last before window open. **The drain total is order-independent; which items miss window 1 is not** — stated where used (§5) | Rebuild's stated convention |

**Cost model (one line):** cost of one transmission = size ÷ effective rate + 5 s turnaround.

**Per-transmission costs under the model:**

| Object / form | Size | Case A (eff. 120 B/s) | Case B (eff. 30 B/s) |
|---|---|---|---|
| Order, whole | 2,000 B | 16.7 + 5 = **21.7 s** | 66.7 + 5 = **71.7 s** |
| Report, whole | 3,000 B | 25.0 + 5 = **30.0 s** | 100.0 + 5 = **105.0 s** |
| Report, delta | 375 B | 3.1 + 5 = **8.1 s** | 12.5 + 5 = **17.5 s** |
| Logistics, whole | 1,500 B | 12.5 + 5 = **17.5 s** | 50.0 + 5 = **55.0 s** |
| Logistics, summary | 400 B | 3.3 + 5 = **8.3 s** | 13.3 + 5 = **18.3 s** |

---

## 3. Rebuild A — the original parameters (HF typical, 1,200 bit/s)

### FIFO baseline (all 12 objects, whole form)

| Line | Arithmetic | Seconds |
|---|---|---|
| Data volume | 2,000 + (5 × 3,000) + (6 × 1,500) = 26,000 B | — |
| Data time | 26,000 ÷ 120 | 216.7 |
| Turnaround | 12 transmissions × 5 s | 60.0 |
| **Total drain** | | **≈277 s ≈ 0.46 of the window** |

(Cross-check on `09`'s own "before turnaround/ARQ" basis: 26,000 ÷ 150 = 173 s ≈ 0.29 of the window; `17`'s 153 s is the same computation on the 11 listed objects.)

### Policy (per A10)

| Line | Arithmetic | Seconds |
|---|---|---|
| Order, whole | 2,000 ÷ 120 + 5 | 21.7 |
| 4 reports as deltas | 4 × (375 ÷ 120 + 5) | 32.5 |
| Superseded report | pruned — never transmitted | 0 |
| 2 logistics as summaries | 2 × (400 ÷ 120 + 5) | 16.7 |
| 4 logistics deferred | held for the next window | 0 |
| **Total spend** | 7 transmissions; 4,300 B of data | **≈71 s ≈ 0.12 of the window** |

### Verdict A — both headlines false; the demonstration fails at these parameters

- "≈2.5 windows under FIFO" → **0.46 of one window**, overhead honestly included. FIFO delivers *everything* — including the superseded report — with ≈323 s of the window to spare.
- "≈ a third of the window" for policy → **≈0.12 of the window**. The true policy figure is *better* than claimed, but the claim as written is unsupported either way.
- What the corrected scenario does show at 1,200 bit/s: policy spends **≈26% of FIFO's bearer-seconds** (71 vs 277 s, a ≈74% saving) for the same decision-relevant deliveries, transmits zero superseded bytes, and defers routine traffic by choice. (A by-product worth knowing: 35 of policy's 71 s is turnaround, not data — at the typical rate, form reduction below delta size buys little; the fixed per-transmission cost dominates.)
- What it does **not** show: prioritization *under scarcity*. At the typical rate the window was never scarce — FIFO's failure mode never occurs, so the scenario cannot demonstrate why the policy matters. **A scenario in which the naive baseline also succeeds demonstrates efficiency, not prioritization.**

---

## 4. Rebuild B — the smallest change that makes a true demonstration

**The change: one parameter.** Plan the scenario against a poor-conditions HF rate of **300 bit/s** instead of the typical 1,200 bit/s. Queue, window, sizes, turnaround and ARQ assumptions — everything else — identical to Rebuild A. 300 bit/s is not an invention: it sits inside the annex's own STANAG 5066 envelope (75–9,600 bit/s), and falling back to a lower in-envelope rate is what the waveform does in poor conditions. The scenario's defect was planning its *degraded* case at the *typical* rate.

### FIFO baseline at 300 bit/s (effective 30 B/s)

| Line | Arithmetic | Seconds |
|---|---|---|
| Data time | 26,000 ÷ 30 | 866.7 |
| Turnaround | 12 × 5 s | 60.0 |
| **Total drain** | | **≈927 s ≈ 1.5 windows** |

Window 1, walked in the stated arrival order (A11):

| Completes at | Item | |
|---|---|---|
| 330 s | 6 logistics messages (6 × 55 s) | routine traffic first — it arrived first |
| 435 s | **the superseded report** (105 s) | bearer-seconds spent on a picture already replaced |
| 540 s | current report #1 (105 s) | |
| 645 s | current report #2 — **misses window 1** | |
| — | current reports #3, #4 and **the order** never start | they wait for window 2; the order's 71.7 s would have fit in window 1 many times over |

Under any arrival order the drain is ≈927 s; the stated order only decides *which* items miss. In the accumulation order a store-and-forward queue actually has, naive FIFO spends the degraded window on routine backlog and a dead report while the top-band order does not cross.

### Policy at 300 bit/s

| Line | Arithmetic | Seconds |
|---|---|---|
| Order, whole | 2,000 ÷ 30 + 5 | 71.7 |
| 4 reports as deltas | 4 × (375 ÷ 30 + 5) | 70.0 |
| Superseded report | pruned | 0 |
| 2 logistics as summaries | 2 × (400 ÷ 30 + 5) | 36.7 |
| 4 logistics deferred | held, with aging | 0 |
| **Total spend** | 7 transmissions; 4,300 B of data | **≈178 s ≈ 0.30 of the window** |

Policy delivers the order, all four current picture changes, and both deadline logistics inside window 1, in ≈19% of the bearer-seconds FIFO would spend — and leaves ≈422 s (70%) of the window unspent, which is the original text's "margin for ARQ and inbound traffic," now actually true.

---

## 5. Sensitivity — the verdict does not rest on the friendly end of any assumption

Rebuild B recomputed with each assumption pushed against the claim, one at a time:

| Variation | FIFO drain | Policy spend | Claim holds? |
|---|---|---|---|
| As stated (§4) | 927 s ≈ 1.5 windows | 178 s ≈ 0.30 window | Yes |
| Turnaround 10 s (top of the stated band, doubled) | 987 s ≈ 1.6 windows | 213 s ≈ 0.36 window | Yes |
| ARQ derating 0.7 instead of 0.8 | 1,050 s ≈ 1.75 windows | 199 s ≈ 0.33 window | Yes |
| Deltas twice as large (750 B) | 927 s (unchanged) | 228 s ≈ 0.38 window | Yes |

---

## 6. Verdict

- **The claim survives — in corrected form, at a stated degraded rate.** The prioritization claim (form chosen at fusion time, supersession pruned, routine traffic deferred by policy) is truly demonstrated by Rebuild B: FIFO needs ≈1.5 windows and, in backlog order, never delivers the order in window 1; policy delivers everything decision-relevant in ≈178 s, ≈30% of one window.
- **Neither original headline survives at any rate.** The honest pair at 300 bit/s is **≈1.5 windows (FIFO) vs ≈0.30 of one window (policy)**. At the original typical rate the honest pair is **≈0.46 of a window (FIFO) vs ≈0.12 (policy)** — a real efficiency result that does not demonstrate prioritization under scarcity.
- **Smallest change:** the bearer rate assumption (typical → stated poor-conditions, in-envelope). No change to the traffic mix, the window, or the model's claims is required. The wording change that must accompany it: the scenario must *say* the rate is a degraded-conditions figure, so a reader does not mistake 300 bit/s for the typical case.

## 7. Adoption text for Oct 21 (paste-ready; `09` is edited only by the session's decision)

**Scenario B, rebuilt (replaces `09` §7's B paragraph if adopted):**

> **B — Degraded (HF only; a predicted 10-minute window; poor conditions hold the bearer at 300 bit/s, inside the STANAG 5066 envelope — ≈22.5 KB raw per window).** Queue at window open: 1 order (whole form 2 KB), 5 situation reports (whole 3 KB each) — one of them an earlier version already superseded by a newer report from the same originator — and 6 routine logistics messages (1.5 KB each). Sent whole in arrival order, that queue needs ≈927 s ≈ 1.5 windows once turnaround and retransmission are charged, and the window it gets is spent in arrival order: the routine backlog and the superseded report cross; the order does not. Policy spends the window differently: the order crosses whole (top band, §3.4); the four current reports cross as **deltas** against last-acknowledged state (≈375 B each), because their value is their *change*, not their restated whole; two logistics messages with near deadlines cross as summaries (≈400 B each); four defer to the next window with aging applied; the superseded report is pruned and never consumes a second. Total spend ≈178 s — about 30% of the window, at ≈19% of the bearer-seconds the whole-form queue would burn — delivering the order, the current picture and the deadline traffic, with the rest of the window held for retransmission and inbound traffic. (Assumptions and arithmetic: file `18`. At the typical 1,200 bit/s the same queue drains whole in ≈277 s and policy spends ≈71 s — the prioritization difference is a degraded-conditions property, and the demonstration is stated at a degraded rate for that reason.)

**Fallback, if the session prefers to keep the typical rate** — replace only the final sentence of `09` §7's B paragraph with: "Total spend ≈71 s of the 600 s window (≈12%), against ≈277 s (≈46%) to send the whole queue in arrival order — the saving comes from form choice and supersession, and the four routine messages are deferred by policy while capacity remains, not by congestion." This wording is true at 1,200 bit/s, but it demonstrates efficiency, not prioritization under scarcity; D-B4 should not be settled on it as if it did.

---

*Prepared 2026-10-16 by the hive, per `17` must-fix #2. All arithmetic shown and independently reproducible from §2's assumptions; decimal-KB convention per `17` C1. Sources: `09` §§2.2, 3.3, 3.4, 6, 7; `07` §1.5; `17` C2. No existing pack file was modified.*
