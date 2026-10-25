# 26 — Clock-bias solver: fractional-domain (ppm) estimator, prototyped and validated (2026-10-16)

**What this is:** file `24` attributed ≈324 Hz of the as-built solver's 340.2 Hz corrected p90 to estimator construction — one bias estimated *in Hz*, pooled across carriers 1176–1605 MHz during a 0.82 ppm clock episode — and proved it with a counterfactual (the unmodified solver run on frequency-scaled residuals). This file lands that counterfactual as a real estimator variant on a branch, and validates it under held-out discipline and a low-bias guard, against the kill criteria stated in its commission. **Status: PROTOTYPE MEASUREMENT RECORD. Branch `wren/clock-bias-ppm-estimator-20261016` (commit `0e4b21865`) in `modu-rf-lab`; the canonical solver is untouched and nothing is merged. Files `05`, `23`, `24` were not edited.**

## 1. Verdict

**The variant lives — it passes both kill criteria, with one named caveat at extreme drift (§3).** Built form: **one shared fractional parameter per epoch** — the as-built solver's own robust procedure (median → MAD hard-rejection at 4.5·MAD → least-squares mean on inliers, same fallbacks) run on carrier-divided residuals dᵢ = rᵢ/fᵢ, each measurement then corrected by δ̂·fᵢ. This is the smaller honest change: the physics has exactly one common-mode degree of freedom (the drift), and the robust procedure carries over verbatim; a per-carrier-Hz fit would spend an epoch's ~43 measurements on up to 9 parameters, is undefined on single-carrier epochs, and changes the solver's interface. The variant is a sibling module (`tools/ghost-sat/clock_correct_frac.py`) importing `clock_correct`'s primitives — `clock_correct.py` itself is byte-identical to the version files `23`/`24` measured (verified by empty diff).

On the anchor capture the variant reproduces the counterfactual's collapse as a landed estimator — pooled corrected **p90 340.2 → 15.7 Hz**, median **17.4 → 7.8 Hz**, per-epoch RMS median **200.9 → 9.9 Hz** — and the collapse is not an in-sample artefact: fitted-window and held-out windows agree (§2). Equivalence to file `24`'s diagnostic is exact to rounding (max per-measurement difference 0.1 Hz over 11,049 measurements; none above 0.2 Hz), so everything file `24` established about the counterfactual now holds of a runnable estimator.

## 2. Numbers — anchor capture (2026-10-12; 266 epochs; 11,049 measurements; ≈0.82 ppm episode)

Sanity anchor first: the as-built arm of this run reproduces files `23`/`24` to the printed digit (raw 1,221.3 / 1,347.0; corrected 17.4 / 340.2; bias 1,286.3; n = 11,049; 266 epochs — `validation.json` records `match: true`).

| Pooled \|residual\| (Hz) | Raw | As-built | Variant |
|---|---|---|---|
| Median | 1,221.3 | 17.4 | **7.8** |
| p90 | 1,347.0 | 340.2 | **15.7** |
| p99 | 1,407.6 | 362.7 | **20.9** |
| Max | 1,438.0 | 461.4 | **147.9** |
| Per-epoch RMS, median | 1,172.3 | 200.9 | **9.9** |

The max (147.9 Hz) is the same fringe L5 point file `24` §2 identified (NORAD 37847, C/N0 3.9 dB-Hz) — under the counterfactual it read −147.9 Hz; the variant agrees. Epoch verdicts under the pipeline's RMS tiers: 266/266 CONSISTENT under both corrected arms (the variant's margin is ~20× wider).

**Strata (median / p90, Hz).** By constellation — variant vs as-built: GPS 6.6/16.1 vs 17.9/344.4 · Galileo 7.1/14.5 vs 14.8/341.2 · BeiDou 7.7/13.5 vs 19.5/339.4 · GLONASS 13.4/18.9 vs 13.2/32.3. By carrier — L5-class 1176.45 MHz (n = 4,169): 6.5/11.5 vs 326.6/351.9 (the artefact stratum, removed); L1-class 1575.42 MHz (n = 5,316): 8.4/16.2 vs 9.1/18.6 (a small real gain even inside the band the pooled fit favoured). GLONASS channels: variant better on five of seven; on the two channels carrying the largest per-SV offsets (1599.75, 1602.56 MHz) its stratum median is worse by ~4–14 Hz — that is the per-SV remainder of §4 showing through, not the common mode, and the variant does not claim it.

**Held-out discipline (fit epochs 1–133, apply 134–266; the estimator is per-epoch, so the split tests temporal generalisation within the arc, as file `24`'s K2 did):**

| Window | n | As-built p90 | Variant p90 |
|---|---|---|---|
| Fit (epochs 1–133) | 5,228 | 349.3 | 15.9 |
| **Held-out (epochs 134–266)** | 5,821 | **323.6** | **15.6** |

Held-out improvement = **308.0 Hz**; in-sample collapse = **324.5 Hz**; ratio **0.949 ≥ 0.80 → kill criterion 1 NOT triggered.** Held-out medians: 17.5 → 7.8 Hz.

## 3. Low-bias guard — honestly bounded

**No genuinely low-bias retained capture exists.** The guard first looked for one: all six retained daily PhoneLab captures (Oct 12–16, ~90 epochs each, rebuilt through file `23`'s exact pipeline) are clock-bias *episodes* — median |bias| 454 to 2,635 Hz — and the production watcher's raw measurements are not retained (file `23` §6, limit 5). The production-typical regime (run-level correction median ≈1 Hz, file `23` §5) is therefore **not directly measured here**; what follows is the prescribed fallback plus a bias-magnitude sweep, and the gap is stated, not papered over.

**Prescribed fallback** — the anchor capture's lowest-bias decile (27 epochs, |bias| 1,191.4–1,210.6 Hz — still 0.76 ppm, the weakest link in this guard and labelled as such): as-built p90 315.2 → variant **15.5 Hz**; median 18.4 → 7.9 Hz. No degradation; the collapse persists at the lowest biases the anchor offers.

**Sweep** — variant vs as-built pooled corrected p90 (Hz), all six captures, rebuilt identically:

| Capture (UTC) | Median bias (Hz) | As-built p90 | Variant p90 | Epochs variant RMS worse |
|---|---|---|---|---|
| 2026-10-13 01:46 | −620.5 | 164.3 | **11.4** | 0 / 90 |
| 2026-10-13 07:19 | −694.0 | 182.9 | **32.8** | 0 / 90 |
| 2026-10-13 18:47 | −712.3 | 186.8 | **9.0** | 0 / 91 |
| 2026-10-14 18:47 | −454.4 | 120.9 | **10.0** | 0 / 90 |
| 2026-10-15 18:46 | +2,634.8 | 1,941.5 | 2,614.8 † | 0 / 89 |
| 2026-10-16 18:45 | −654.9 | 172.5 | **9.2** | 0 / 90 |

Across the sweep the variant's per-epoch RMS — the statistic the pipeline actually verdicts on — is **never worse than the as-built's in any of the 540 epochs** (largest per-epoch delta is negative everywhere). The two estimators' corrections differ by a term proportional to the drift itself (δ̂·(fᵢ − f_ref) vs a constant), so their disagreement vanishes as drift → 0; the measured trend agrees (at the lowest measured bias, 454 Hz, the variant already improves p90 12×). That scaling statement is an argument, labelled as one; the empirical floor of this guard is 454 Hz, and the 454 → ~1 Hz interval is unmeasured on retained data. **Kill criterion 2 (any low-bias-regime degradation): NOT triggered** on any evidence the retained data can produce.

† **The g5 exception, diagnosed, not buried.** The Oct 15 capture (+1.67 ppm, twice the anchor's drift) is the one pooled-p90 reversal. Its ≥p90 tail in *both* arms is a single non-clock sub-population: three BeiDou SVs (44204, 41434, 38251 — absent from the anchor capture) carrying ≈ **+2.0–2.3 ppm on top of the clock drift** (signed fractional ≈3.9 ppm vs the clock's 1.73), ~10% of the capture's mass, sitting at 1.9–3.7 kHz after *either* estimator. Neither estimator models it; the pooled ordering flips only because the as-built's Hz fit (21/36 inliers in the worst epochs) leans toward the cluster while the variant fits the true common mode (31/36 inliers). On per-carrier medians the variant is better on 8 of g5's 10 carriers, and its per-epoch RMS is ≤ the as-built's in all 89 epochs (median 1,056.9 vs 1,070.6 Hz). Cause of the BeiDou offset is **not established** (candidates: prediction-side error for those SVs that day; a device tracking state — named as candidates only). Lesson carried to §6: pooled p90 alone is not a safe regression metric for this solver when a non-clock cluster reaches ~10% of mass; judge on strata and per-epoch RMS. Smaller p99 tails of the same character persist under the variant in three other captures (p99 301 / 881 / 897 Hz) — unmodelled by either estimator, not separately diagnosed.

## 4. Persistence — the per-SV remainder survives, unmodelled

Per-SV signed median offsets computed on the variant's corrected series (anchor capture) are **still there**: 22 SVs at |offset| ≥ 3 Hz, spanning **−19.7 to +16.8 Hz**. The GLONASS per-channel family of file `24` reads −19.7 (39155) / +15.7 (44299) / +14.6 (46805) Hz — magnitudes matching file `24`'s 15–20 Hz family (39155's signed value is negative in this run). Lag-1 autocorrelation of the per-SV L1-band series, Fisher-z pooled over 21 SVs: **0.526** under the variant vs 0.357 as-built — once the carrier artefact is removed the offsets are *more* stable within the arc, not less. The variant has no per-SV parameter and fits none of this away, by design: these remain file `24`'s unlicensed remainder, and any future per-SV stage must still re-pass K2 across sessions on the corrected series before it is built. (File `24`'s diagnostics showed the same offsets are predictive *within* this arc once the artefact is removed — 82–85% held-out cuts on the corrected/L1 series — which is a statement about this arc, not a licence.)

## 5. Bounded claim wording (for the Oct 20–22 sessions to adopt verbatim, or not)

*"On a retained 266-epoch GNSS capture (11,049 measurements, 2026-10-12) carrying a ≈0.82 ppm receiver clock bias, a fractional-domain variant of the clock-bias solver — one shared drift parameter per epoch, estimated with the as-built solver's own robust procedure on carrier-divided residuals — reduces the pooled corrected p90 from 340.2 Hz to 15.7 Hz and the pooled corrected median from 17.4 Hz to 7.8 Hz against the as-built Hz-pooled solver on identical predictions. Fitted on epochs 1–133 and applied to epochs 134–266, its held-out p90 is 15.6 Hz (a 308.0 Hz improvement, 95% of the in-sample collapse). Across five further retained captures (median clock biases 454–712 Hz) its corrected p90 improves on the as-built's in every capture, and its per-epoch RMS is never worse than the as-built's in any of 540 sweep epochs. Stable per-satellite offsets of ±3–20 Hz survive the variant unmodelled."*

It does **not** support: a typical-epoch figure (the production stream is usually ≈1 Hz bias — file `23` §5 — and no retained capture measures that regime; the guard's empirical floor is 454 Hz); a pooled-p90 claim at extreme drift (at 1.67 ppm a non-clock BeiDou sub-population dominates both estimators' tails, §3†); any per-SV-offset fix (file `24` K2 stands); a geolocation figure. Note also that file `23` §6 limit 4's "a ppm-domain variant would be marginally tighter" is superseded by this measurement: in bias episodes the variant is ≈20× tighter at p90 — it is the largest solver-side lever the attribution priced (≈324 Hz), ahead of precise ephemeris (≈4 Hz) and timestamp alignment (3–13 Hz), and the only one that is solver-internal.

## 6. Method annex

- **Code.** Repo `modu-rf-lab` (Legion), branch **`wren/clock-bias-ppm-estimator-20261016`** off `wren/ghost-journal-changeonly-20261012` @ `c13525d10` (the branch files `23`/`24` used; `clock_correct.py` verified byte-identical to their `44c31c71` version by empty diff), variant committed as `0e4b21865` in a worktree — the main checkout was never switched and the canonical solver is untouched; nothing merged, nothing pushed. New module `tools/ghost-sat/clock_correct_frac.py` (175 lines): imports `median`, `mad`, `MAD_K`, `MIN_SATS_FOR_BIAS` from `clock_correct`; mirrors `estimate_clock_bias` step-for-step in the fractional domain (the degenerate-MAD test is exact-zero in fractional units, where typical MAD ≈ 1e-8; the applied drift is the estimate rounded to 0.1 Hz at the 1575.42 MHz reference carrier, mirroring the as-built rounding; corrections rounded to 0.1 Hz as in `correct_epoch`). The reference carrier scales only the *reported* bias — the correction δ̂·fᵢ is reference-free.
- **Datasets.** Anchor: file `24`'s rebuilt per-measurement dataset (`rows.jsonl`, sanity-matched to file `23`; this run's as-built arm re-matched it — §2). Guard captures: six retained PhoneLab captures rebuilt with file `23`'s exact parse, 250 ms clustering, mapping, 10° mask and solver call (`guard_dump.py` = `tail_dump.py` with capture constants changed) — Oct 13 01:46Z / 07:19Z / 18:47Z, Oct 14 18:47Z, Oct 15 18:46Z, Oct 16 18:45Z; 89–91 qualifying epochs each; TLEs from the estate's cached CelesTrak set (current cache, propagated to each capture date — the paired-arm design makes every comparison insensitive to prediction error common to both arms). No synthetic data anywhere in the validation; the module's `__main__` smoke test is a code check in `clock_correct.py`'s own estate pattern and is not evidence.
- **Statistics.** Files `23`/`24` conventions throughout (nearest-rank percentiles, 0.1 Hz rounding of reported distributions; pooled = per-measurement |residual|). Held-out split and kill bars exactly as commissioned: kill if held-out p90 improvement < 80% of the in-sample collapse (measured: 94.9%), or any low-bias-regime degradation (measured: none producible from retained data — §3 states the construction and its floor).
- **Equivalence check.** The variant was also run against file `24`'s counterfactual construction (scale by F₀/fᵢ, F₀ = 1575420032, unmodified solver, map back) on the anchor: pooled 7.8/15.8 Hz vs the variant's 7.8/15.7; per-measurement |difference| max 0.1 Hz, mean 0.017 Hz, zero above 0.2 Hz — the landed estimator *is* the counterfactual, to rounding conventions.
- **Artefacts (Legion, `/home/jason/solver-ppm-20261016/`, beside `/home/jason/solver-replay-20261016/` and `/home/jason/solver-tail-20261016/`):** the branch worktree (`modu-rf-lab-wt/`), `validate_ppm.py` + `validation.json` (every number in §§2–4), `guard_dump.py`/`guard_dump2.py` + `rows_guard*.jsonl` + `guard_summary*.json` + `tle_info_guard*.json`, `diag_g5.py`/`diag_g5b.py` (the §3† diagnosis), run logs. All runs read-only against inputs, detached; no transmissions.
