# 23 — Clock-Bias Solver: measured delta on recorded data (offline replay, 2026-10-16)

**What this is:** the first first-hand performance measurement of the estate's receiver clock-bias solver (`clock_correct.py`, modu-rf-lab), produced by replaying recorded raw GNSS measurements through the pipeline's own prediction path twice — once with the recorded residuals untouched, once with the solver applied per epoch. It exists because draft `05` (¶3) and the evidence map (TRL row C3) claim the solver by existence only; no quantified solver-performance number existed anywhere in this pack before this file. **Status: MEASUREMENT RECORD. Nothing in `05` was edited; §7 states exactly which vault rows this evidence speaks to and the bounded claim wording it supports.**

## 1. Headline result

Dataset: one recorded PhoneLab capture session, 2026-10-12 (full statement in §2). 266 qualifying epochs; 11,049 usable satellite measurements; every qualifying epoch in the capture was used — no selection.

| Statistic (absolute Doppler residual vs TLE/SGP4 prediction, Hz) | Raw (as recorded) | Solver-corrected | Delta |
|---|---|---|---|
| Pooled per-measurement median (n = 11,049) | **1,221.3** | **17.4** | **~70× lower** |
| Pooled per-measurement p90 | 1,347.0 | 340.2 | ~4.0× lower |
| Pooled per-measurement max | 1,438.0 | 461.4 | — |
| Per-epoch RMS, median over 266 epochs | 1,172.3 | 200.9 | ~5.8× lower |
| Epoch verdicts under the pipeline's own RMS tiers (`compare.py`: <500 Hz CONSISTENT; 500–5,000 NEEDS_INVESTIGATION; >5,000 GHOST_CANDIDATE) | 266 NEEDS_INVESTIGATION | 266 CONSISTENT | **266 / 266 epochs flip** |

The solver's per-epoch bias estimates in this capture: |bias| median **1,286 Hz** (p90 1,374; max 1,405) at L1-equivalent ≈ **0.82 ppm** receiver clock drift ≈ **245 m/s** of common-mode range-rate error carried by every satellite in the epoch before correction. In range-rate terms the pooled median residual falls from ≈232 m/s (raw) to ≈3.3 m/s (corrected). All 266 epochs were solved by the solver's robust path (`robust_ls`); no epoch fell back to the median path.

**The regime matters as much as the number (see §6):** this capture sits in a large, stable clock-bias episode — close to the solver's best case. The catalogue-scale panel (§5) shows the production stream is usually low-bias, so this delta describes what the solver does *when an epoch carries real clock bias*, which is precisely the condition under which uncorrected epochs poison every satellite's verdict at once. It must not be quoted as a typical-epoch improvement.

## 2. Dataset (exact)

- **Source files (Legion):** `/home/jason/phone-mine/p9_pull_20261012/phonelab-captures/20261012T194749Z/` — `phonelab_gnss_20261012_124625.jsonl` (4,183 raw measurements; sha256 `801b1475…` per the capture's own `capture_report.json`) and `phonelab_gnss_20261012_124751.jsonl` (9,256 raw measurements; sha256 `a9fc2a61…`). This is the same capture the vault already cites (evidence-map C5: "9,256 raw GNSS measurements in a single quality-gated capture" — that count is the second file alone; both files are one pull, one session).
- **Window:** 2026-10-12T19:46:26Z → 19:50:52Z (4 min 26 s), Pixel 9 PhoneLab collector, West Kelowna. Observer coordinates as used by the production watcher: lat 49.8269, lon −119.6479, alt 450 m.
- **Truth source:** GNSS satellites — public precise-orbit-class transmitters. Predictions are the pipeline's own: CelesTrak TLE + SGP4 (`predict.py`/`doppler.py`), i.e. the same predictions the live pipeline fuses against — not IGS precise ephemerides (limit, §6).
- **Accounting (no silent drops):** 13,439 `raw_measurement` records parsed. Usable signed residuals: **11,049**. Excluded: 1,566 measurements the pipeline cannot map to a NORAD/frequency (SBAS 244/244 and QZSS 346/346 — no mapping table exists for those constellations; Galileo 976 of 4,137 — SVs absent from the cached mapping) and 824 below the pipeline's 10° elevation mask. Records by constellation: GPS 3,981; GLONASS 2,067; BeiDou 2,664; Galileo 4,137; QZSS 346; SBAS 244.
- **Epochs:** measurements clustered by record timestamp (new epoch when the gap exceeds 250 ms; within-batch gaps are 0–1 ms, inter-batch ~1 s) → 267 clusters; **266 qualify** (≥4 usable satellites — the solver's own `MIN_SATS_FOR_BIAS`); 1 cluster had 1–3 usable satellites and is excluded from both arms. Median 43 satellites per qualifying epoch (max 46), 28 distinct NORADs used: GPS, GLONASS, Galileo, BeiDou.

## 3. Method (so the Oct 22 vault pass can cite and re-run it)

- **Code path (estate code, unmodified):** repo `modu-rf-lab` (Legion, `/home/jason/Projects/github/modu-rf-lab`), branch `wren/ghost-journal-changeonly-20261012`, HEAD `44c31c712d47596608c3bfb81d30ab56a9a30ef9`; solver file `tools/ghost-sat/clock_correct.py` (last commit `e90acd09e`, 2026-10-11). Working tree for `tools/ghost-sat/` verified clean at replay time.
- **Residual construction:** each raw measurement → `gnss_doppler.measurement_to_observed()` (the pipeline's own PhoneLab mapping: SV→NORAD via the cached SV mapping; observed Doppler = −pseudorangeRate × carrierFreq / c, stock sign convention) → signed residual via `compare._signed_epoch_residual()` (predicted Doppler from TLE/SGP4 at the measurement timestamp, pipeline elevation mask applied). TLEs are the Legion's cached CelesTrak set (`~/.cache/modu-ghost-sat/tle/`); TLE epoch ages for the 28 satellites used: median 2.5 days (one satellite, NORAD 41859, carried a 23.1-day-old TLE — §4). Both arms use identical predictions, so the delta is insensitive to prediction error by construction.
- **Arms:** RAW = signed residuals exactly as recorded. SOLVER = `clock_correct.correct_epoch()` applied per epoch (median + MAD-scaled hard-rejection IRLS at 4.5·MAD, least-squares mean on inliers, bias subtracted from every residual in the epoch — the solver's designed per-epoch operating point). The solver is the only difference between arms.
- **Statistics:** pooled per-measurement |residual| median/p90/p99/max; per-epoch RMS (the statistic `compare.py`'s epoch tiers verdict on) with verdict counts under those tiers; per-constellation medians; per-satellite medians/p90. Verdict tiers: `RMS_CONSISTENT_HZ = 500`, `RMS_GHOST_HZ = 5000` (`compare.py`).
- **Commands / artefacts (Legion):** scripts + outputs in `/home/jason/solver-replay-20261016/`: `replay_solver_delta.py` → `replay_results.json` + `replay.log`; `replay_addon.py` → `replay_addon.json` (per-satellite detail); `verdicts_panel.py` + `panel_pairs.py` → `verdicts_panel.json` / `verdicts_pairs.json` (§5). Run detached (`legion-detached.py`, systemd user units), read-only against all inputs; no transmissions; no new hardware.

## 4. Results in full

- **Bias estimated per epoch:** |bias| median 1,286.3 Hz, p90 1,374.3, p99 1,403.0, max 1,405.0 (n = 266) — a large and *stable* offset across the whole session (≈0.8–0.9 ppm). Stability is itself evidence the common mode is the receiver clock, not geometry: a position or frame error would not present as one near-constant scalar shared by 43 satellites across four constellations.
- **Per-constellation pooled median |residual| (Hz):** GPS 1,213.2 → 17.9 (n = 3,979); GLONASS 1,295.6 → 13.2 (n = 1,564); Galileo 1,196.4 → 14.8 (n = 3,161); BeiDou 1,198.9 → 19.5 (n = 2,345). The correction is not a one-constellation artefact.
- **Corrected tail (reported, not hidden):** corrected p90 is 340.2 Hz while the median is 17.4 Hz — in a typical epoch a rotating minority of satellites carries ~300–460 Hz residuals the solver by design cannot remove (it removes only the common mode). This tail is what holds corrected epoch RMS at ~201 Hz median. Per-satellite: most satellites' corrected medians are 0.4–32 Hz; three retain elevated medians — NORAD 41859 (315.7 Hz; its TLE was 23.1 days old — a plausible prediction-side cause), NORAD 39741 (310.5 Hz) and NORAD 40534 (155.3 Hz), both on fresh TLEs (2.3–2.4 days) with no cause established by this replay. Root-causing the per-satellite tail is a follow-on measurement, not claimed here.
- **Sign convention check:** the stock pipeline convention was used throughout. It is self-validating in this data: the opposite convention yields residuals on the order of twice the Doppler (tens of kHz) with no common-mode structure for a constant subtraction to collapse to 17 Hz.

## 5. Catalogue-scale context panel (what regime the solver usually faces)

The capture above is one session. For the operating regime at catalogue scale, the production watcher's own run log was streamed read-only: `/home/jason/workspace/goals/satellite-operations-ghost-sat-passes/hidden_files/ghost_verdicts.jsonl` — **474 runs, 2026-10-10T09:49Z → 2026-10-17T03:17Z, 908,793 measurements** (the log behind the live catalogue).

- The watcher's applied per-run clock correction (a run-level median, a separate coarser layer than the solver): |correction| median **1.0 Hz**, p90 10.8 Hz, max 1,630.1 Hz. Only **8 of 474 runs** applied ≥100 Hz — seven on 2026-10-10 (the solver-integration week; biases +1,538…+1,630 Hz and −613 Hz) and one on 2026-10-13 (−140 Hz).
- Reading: the production stream is **usually low-bias**; large clock-bias episodes are episodic (integration week; the §2 capture) but when present they are kilohertz-scale and hit every satellite simultaneously. The solver's value concentrates in those episodes. One clean paired case from the log: 2026-10-10T10:09Z run, bias −613 Hz, analyze median residual 612.8 → 13.7 Hz after correction.
- What this panel cannot do: the log's paired raw/corrected summaries both come from `analyze()`, which applies the solver internally in both passes — so the summary pairs **do not isolate `clock_correct.py`** and are not used as solver evidence here. In five of the earliest (2026-10-10) runs the two correction layers interfered and the corrected-pass median was *worse* (~1.6 kHz → ~2.1 kHz); recorded as an integration-era artefact of the layered stack, and a reason the controlled two-arm replay (§3) is the citable instrument rather than the production log.
- A prior estate record is consistent with the replay: `tools/ghost-sat/doppler-clock-correction-20261010.md` records 30/30 NEEDS_INVESTIGATION epochs flipping to CONSISTENT on the 2026-10-10 trigger epoch when the correction was first integrated. That note is secondhand corroboration; §1's numbers are this replay's own.

## 6. What this does and does not establish

**Established (first-hand, this replay):** on recorded data carrying a real receiver clock bias, the solver removes the common-mode bias and reduces per-measurement Doppler residuals by ~70× at the median (1,221 → 17 Hz) and per-epoch RMS by ~5.8×, moving every affected epoch out of the pipeline's investigation band. The bias magnitudes it handles in the recorded estate data reach ~1.6 kHz (≈0.9 ppm).

**Not established / limits:**
1. **One session.** The replay window is a single 4 min 26 s capture at one site with one receiver. It demonstrates the solver in a strong-bias regime; §5 bounds how often that regime occurs in the catalogue stream. A multi-session replay (bias episodes harvested from the watcher log's high-bias runs, if their raw measurements are retained) is the follow-on that would widen the envelope.
2. **Doppler/timing domain only.** The estate's recorded data is single-receiver; there is no multi-receiver geometry in it, so no geolocation accuracy was measured and none may be inferred. The residual measured here is the per-detection timing-domain residual the fusion design consumes.
3. **Predictions are TLE/SGP4**, the pipeline's own truth reference — adequate for a paired delta (identical in both arms), but the absolute corrected floor (17 Hz median) includes prediction error and is not a solver-only floor.
4. **Hz-pooling note:** the solver estimates one bias in Hz pooled across constellations; a true clock drift scales with carrier frequency, so pooling leaves a small known cross-constellation remainder (≤ ~35 Hz worst case at this drift) inside the corrected floor. A ppm-domain variant would be marginally tighter; the as-built solver is what was measured.
5. **Catalogue DB rows were not used as replay input**: the catalogue stores post-correction verdicts (the production stack corrects before logging), so raw residuals are not recoverable from it — the replay correctly used the retained raw capture instead. Any future claim about catalogue-wide solver effect must start from raw captures or the watcher log, not from `observations.db`.
6. The corrected per-satellite tail (§4) is measured and disclosed; its cause is not established.

**Bounded claim wording this evidence supports** (for the design sessions / Oct 22 to adopt or not): *"In a recorded 266-epoch GNSS capture (11,049 satellite measurements, 2026-10-12) carrying a ≈1.29 kHz receiver clock bias (0.82 ppm), the receiver clock-bias solver reduced the median absolute Doppler residual against TLE/SGP4 prediction from 1,221 Hz to 17 Hz and moved all 266 epochs from the pipeline's NEEDS_INVESTIGATION band to CONSISTENT."* It does **not** support: a typical-epoch improvement figure, a geolocation accuracy figure, or a catalogue-wide percentage.

## 7. Vault mapping

- **Strengthens evidence-map row C3** ("Ghost-satellite detection pipeline with receiver clock-bias solver; live catalogue", graded LIVE): the row previously rested on catalogue counts and pipeline existence. It now has a first-hand, reproducible solver-performance measurement behind the solver half of the claim (this file; artefacts in `/home/jason/solver-replay-20261016/` on the Legion).
- **Dataset provenance:** the replay's input capture is the artefact already cited at evidence-map C5 / vault B8 (PhoneLab capture 2026-10-12) — no new dataset was created.
- **Proposal `05` ¶3:** the solver sentence there is existence-level and stays accurate as written; §6's bounded wording is available if the design sessions choose to give it the number.
- **X-rows (vault INDEX X1–X8): none is a solver-performance claim, and this evidence closes none of them** — Oct 22's fix-or-soften work on X1–X8 is unchanged. What this retires is the gap that would otherwise have forced a new EXPOSED row for any quantified solver claim; claims beyond §6's bounded wording would re-open it.
