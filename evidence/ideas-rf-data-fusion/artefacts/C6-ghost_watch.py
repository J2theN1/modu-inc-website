#!/usr/bin/env python3
"""ghost_watch.py — continuous ghost-satellite verdict loop.

Wires the live P9 Doppler tracker into the ghost-sat detection pipeline:

    P9 DopplerTracker (56 sats / 5s, SQLite)
        -> adb pull to Legion
        -> gnss_doppler.analyze()  (SV->NORAD, PRR->Doppler Hz, SGP4 predict)
        -> compare.py verdicts      (CONSISTENT / NEEDS_INVESTIGATION / GHOST_CANDIDATE)
        -> ghost_verdicts.jsonl     (append-only log)
        -> observations.db          (durable per-measurement catalog, idempotent)

Usage:
    python3 ghost_watch.py [--epochs N] [--db PATH]

Exit codes: 0 = clean (no ghosts), 2 = GHOST_CANDIDATE found, 1 = error.
"""
import atexit
import json
import os
import shutil
import sqlite3
import subprocess
import sys
import tempfile
import time
from datetime import datetime, timezone

ADB = "adb"
P9_SERIAL = "192.168.1.91:5555"
P9_DOPPLER_DIR = "/data/local/tmp/doppler"
GHOST_SAT_DIR = os.path.expanduser(
    "~/Projects/github/modu-rf-lab/tools/ghost-sat")
OUT_DIR = os.path.expanduser(
    "~/workspace/goals/satellite-operations-ghost-sat-passes/hidden_files")
VERDICTS_LOG = os.path.join(OUT_DIR, "ghost_verdicts.jsonl")

# P9 balcony location (from field reports), West Kelowna BC
OBS_LAT, OBS_LON, OBS_ALT_M = 49.8269, -119.6479, 450.0

sys.path.insert(0, GHOST_SAT_DIR)


def pull_latest_db(tmpdir):
    """Pull today's Doppler DB from P9 via SQLite backup API.

    The DB is LIVE (DopplerTracker writes continuously). Raw cp of a live
    SQLite DB produces torn pages -> corrupt copy. Use the on-device
    sqlite3 backup API to snapshot first, then pull the snapshot.
    """
    today = datetime.now().strftime("%Y%m%d")
    remote = f"{P9_DOPPLER_DIR}/doppler_{today}.db"
    snapshot = "/data/local/tmp/ghost_watch_snapshot.db"
    staged = f"/sdcard/ghost_watch_{today}.db"
    local = os.path.join(tmpdir, f"doppler_{today}.db")

    def run(*args, timeout=60):
        return subprocess.run(list(args), capture_output=True,
                              text=True, timeout=timeout)

    # Verify the DB exists; fall back to newest doppler_*.db on device
    r = run(ADB, "-s", P9_SERIAL, "shell",
            f"ls {P9_DOPPLER_DIR}/doppler_{today}.db 2>/dev/null || "
            f"ls -t {P9_DOPPLER_DIR}/doppler_*.db 2>/dev/null | head -1")
    lines = r.stdout.strip().splitlines()
    remote = lines[0].strip() if lines else ""
    if not remote:
        raise RuntimeError("no doppler DB found on P9")
    # Snapshot via SQLite backup API (torn-page safe), then stage via /sdcard
    # (snapshot is root-owned; adbd runs as shell)
    # The DopplerTracker writes every ~2s; the on-device .backup can hit a
    # transient "database is locked". Retry with backoff instead of failing
    # the whole run (seen 2026-10-11: one 5-min cycle lost per lock hit).
    last_err = ""
    for attempt in range(5):
        r = run(ADB, "-s", P9_SERIAL, "shell",
                "su -c '/data/local/tmp/sqlite3 " + remote + " \".backup main " + snapshot + "\""
                " && cp " + snapshot + " " + staged +
                " && chmod 644 " + staged +
                " && rm -f " + snapshot + "'", timeout=180)
        if r.returncode == 0:
            break
        last_err = (r.stdout + " " + r.stderr).strip()
        if "database is locked" in last_err.lower():
            time.sleep(2 * (attempt + 1))
            continue
        raise RuntimeError("on-device backup failed: %s" % last_err)
    else:
        raise RuntimeError(
            "on-device backup failed after 5 attempts: %s" % last_err[:200])
    r = run(ADB, "-s", P9_SERIAL, "pull", staged, local, timeout=180)
    run(ADB, "-s", P9_SERIAL, "shell", f"rm -f {staged}")
    if r.returncode != 0 or not os.path.exists(local):
        raise RuntimeError(f"adb pull failed: {r.stderr.strip()}")
    # Integrity gate before use
    chk = subprocess.run(
        ["sqlite3", local, "PRAGMA integrity_check;"],
        capture_output=True, text=True, timeout=60)
    if "ok" not in chk.stdout.lower():
        raise RuntimeError(
            f"pulled DB failed integrity check: {chk.stdout.strip()[:100]}")
    return local


def load_measurements(db_path, n_epochs=60):
    """Read the last n_epochs of measurements. Returns meas dicts."""
    con = sqlite3.connect(f"file:{db_path}?mode=ro", uri=True)
    cur = con.cursor()
    cur.execute(
        "SELECT epoch_id, wall_time_ms FROM epochs "
        "ORDER BY epoch_id DESC LIMIT ?", (n_epochs,))
    epochs = cur.fetchall()
    if not epochs:
        con.close()
        return []
    epoch_ids = [e[0] for e in epochs]
    ts_by_epoch = {e[0]: e[1] for e in epochs}
    q = ("SELECT epoch_id, svid, constellation, pr_rate_mps FROM measurements "
         "WHERE epoch_id IN (%s) AND pr_rate_mps IS NOT NULL"
         % ",".join("?" * len(epoch_ids)))
    cur.execute(q, epoch_ids)
    meas = []
    for epoch_id, svid, const, prr in cur.fetchall():
        wall_ms = ts_by_epoch[epoch_id]
        ts_utc = datetime.fromtimestamp(wall_ms / 1000.0,
                                        tz=timezone.utc).isoformat()
        meas.append({"svid": svid, "constellation": const,
                     "prr_m_s": prr, "timestamp_utc": ts_utc})
    con.close()
    return meas


JOURNAL_SOURCE = "ghost-watch"

# Change-only journaling state: the previous run's journal-relevant
# verdict set, persisted alongside ghost_verdicts.jsonl in OUT_DIR.
# _persist_run writes per-measurement rows to the observations.db
# catalog and main() appends the CURRENT run to ghost_verdicts.jsonl
# before _journal_run is called, so neither store offers a clean
# previous-run baseline at the journaling point; this small state
# file is that baseline.
JOURNAL_STATE = os.path.join(OUT_DIR, "ghost_watch_journal_state.json")

# A satellite that stays STALE_TLE re-journals only when its TLE age
# crosses into a new band of this many hours (~weekly). The stale
# condition itself is already known after the transition entry; a
# TLE still unfixed a band later is materially worse, so it earns
# exactly one more entry per band, not one per 15-min cycle.
STALE_AGE_BAND_HOURS = 168.0


def _journal_state_load(path):
    """Return the persisted previous-run journal state, or None when
    there is no usable baseline (first run ever / corrupt file)."""
    try:
        with open(path) as f:
            state = json.load(f)
        if isinstance(state, dict) and isinstance(
                state.get("verdicts"), dict):
            return state
    except Exception:
        pass
    return None


def _journal_state_save(path, run, verdicts, names, stale_ages):
    """Persist this run's journal-relevant verdict set as the next
    run's baseline (atomic tmp+rename). Best-effort: the caller
    swallows failures, so a lost save only re-journals a transition
    once on the next run (the serendipity dedupe collapses repeats).
    """
    state = {"version": 1, "run_utc": run.get("run_utc"),
             "verdicts": verdicts, "names": names,
             "stale_age_hours": stale_ages}
    os.makedirs(os.path.dirname(path), exist_ok=True)
    tmp = path + ".tmp"
    with open(tmp, "w") as f:
        json.dump(state, f, sort_keys=True)
    os.replace(tmp, path)


def _journal_run(run, ghosts, _log=None, _state_path=None):
    """Append serendipity-journal entries for one completed run --
    but only when the run's verdict set CHANGED vs the previous run.

    The Oct 12 harvest audit found ~34 of 43 ghost-watch journal
    entries were routine cycle summaries whose own text said
    "informational only, no action needed", journaled every ~15 min.
    The journal -> job-board bridge triages entries by source and
    text, so that flood cost triage attention and spawned duplicate
    TLE-refresh jobs, while the lane's real value -- STALE_TLE
    downgrades and GHOST_CANDIDATEs -- is transitional by nature.

    The rule (journal-relevant verdict set = one verdict per NORAD
    id, restricted to GHOST_CANDIDATE and STALE_TLE; CONSISTENT /
    count churn is routine and never journals):

    - First run ever (no readable baseline state): journal exactly
      as the pre-change code did (routine summary, ghost entries,
      stale entry) -- that entry set is the baseline.
    - A NORAD newly GHOST_CANDIDATE: the legacy urgent ghost entry
      (unchanged wording; still the >= 85 push path).
    - A NORAD whose GHOST_CANDIDATE cleared: one informational
      clearing entry.
    - A NORAD newly STALE_TLE: the legacy STALE_TLE entry (unchanged
      wording; still the TLE-refresh action), naming only the newly
      stale objects.
    - A NORAD whose STALE_TLE recovered (no longer stale and not a
      ghost): one informational recovery entry.
    - Material change while stale: a still-stale NORAD whose TLE
      age crosses into a new STALE_AGE_BAND_HOURS band re-journals
      in the STALE_TLE entry, once per band.
    - Anything else -- above all a routine cycle whose verdict set
      is identical to the previous run's -- journals NOTHING.

    The state file is updated every run (after the journal calls),
    so the comparison baseline is always the previous run. If a
    journal call raises, the state is NOT advanced, so the
    transition is retried on the next run.

    Results are per-measurement rows, so the same object can appear
    several times; entries are deduped to one per NORAD id (largest
    |residual| row wins) before journaling.

    Best-effort by contract: journaling must never break the watch
    loop, so everything here is wrapped and swallowed.
    """
    try:
        if _log is None:
            sys.path.insert(0, os.path.expanduser("~/.local/bin"))
            from modu_serendipity import log_serendipity as _log
        if _state_path is None:
            _state_path = JOURNAL_STATE
        s = run.get("corrected_summary") or {}
        vc = s.get("verdict_counts") or {}
        counts = ", ".join("%s=%d" % (k, vc[k]) for k in sorted(vc))
        results = run.get("corrected_verdicts") or []
        stale = [r for r in results if r.get("verdict") == "STALE_TLE"]

        def _best_by_norad(rows):
            best = {}
            for r in rows:
                key = r.get("norad_id")
                res = abs((r.get("details") or {}).get(
                    "doppler_residual_hz") or 0)
                cur = best.get(key)
                if cur is None or res > abs((cur.get("details") or {}).get(
                        "doppler_residual_hz") or 0):
                    best[key] = r
            return list(best.values())

        uniq_ghosts = _best_by_norad(ghosts)
        uniq_stale = _best_by_norad(stale)

        # Current journal-relevant verdict set, one verdict per NORAD
        # (GHOST_CANDIDATE wins if an object somehow carries both).
        cur_verdicts, cur_names, cur_stale_ages = {}, {}, {}
        for r in uniq_stale:
            key = str(r.get("norad_id"))
            cur_verdicts[key] = "STALE_TLE"
            cur_names[key] = r.get("name")
            age = (r.get("details") or {}).get("tle_age_hours")
            if age is not None:
                cur_stale_ages[key] = age
        for r in uniq_ghosts:
            key = str(r.get("norad_id"))
            cur_verdicts[key] = "GHOST_CANDIDATE"
            cur_names[key] = r.get("name")

        prev = _journal_state_load(_state_path)
        baseline = prev is None
        prev_verdicts = (prev or {}).get("verdicts") or {}
        prev_names = (prev or {}).get("names") or {}
        prev_ages = (prev or {}).get("stale_age_hours") or {}

        def _band(age):
            return None if age is None else int(
                age // STALE_AGE_BAND_HOURS)

        new_ghosts = [g for g in uniq_ghosts
                      if prev_verdicts.get(str(g.get("norad_id")))
                      != "GHOST_CANDIDATE"]
        cleared_ghosts = [k for k, v in prev_verdicts.items()
                          if v == "GHOST_CANDIDATE"
                          and cur_verdicts.get(k) != "GHOST_CANDIDATE"]
        band_crossed = {k for k, age in cur_stale_ages.items()
                        if prev_verdicts.get(k) == "STALE_TLE"
                        and _band(age) != _band(prev_ages.get(k))}
        new_stale = [r for r in uniq_stale
                     if prev_verdicts.get(str(r.get("norad_id")))
                     != "STALE_TLE"
                     or str(r.get("norad_id")) in band_crossed]
        recovered = [k for k, v in prev_verdicts.items()
                     if v == "STALE_TLE" and k not in cur_verdicts]

        if not baseline and not (new_ghosts or cleared_ghosts
                                  or new_stale or recovered):
            # Routine cycle, verdict set unchanged: journal nothing.
            _journal_state_save(_state_path, run, cur_verdicts,
                                cur_names, cur_stale_ages)
            return

        ghost_entries = uniq_ghosts if baseline else new_ghosts
        if ghost_entries:
            for g in ghost_entries[:3]:
                d = g.get("details") or {}
                meta = g.get("_meta") or {}
                age = d.get("tle_age_hours")
                _log(JOURNAL_SOURCE,
                     "GHOST_CANDIDATE survived correction: NORAD %s (%s), "
                     "svid=%s %s, Doppler residual %s Hz over %s epochs, "
                     "TLE age %s. Run totals: %s analyzed (%s)."
                     % (g.get("norad_id"), g.get("name"),
                        meta.get("svid"), meta.get("constellation"),
                        d.get("doppler_residual_hz"), d.get("epoch_count"),
                        ("%s h" % age) if age is not None else "unknown",
                        s.get("n_analyzed"), counts),
                     "URGENT: ghost-satellite candidate needs immediate "
                     "human review -- verify against a fresh TLE and a "
                     "second observation window. Concrete investigation "
                     "for a worker.")
            if len(ghost_entries) > 3:
                _log(JOURNAL_SOURCE,
                     "ghost-watch: %d further distinct GHOST_CANDIDATE "
                     "objects in the same run (see ghost_verdicts.jsonl %s)"
                     % (len(ghost_entries) - 3, run.get("run_utc")),
                     "URGENT: multiple ghost-satellite candidates in one "
                     "run need human review.")
        elif baseline:
            _log(JOURNAL_SOURCE,
                 "ghost-watch run: %s analyzed, %s measured; verdicts: %s; "
                 "median residual %s Hz; no surviving ghost candidates"
                 % (s.get("n_analyzed"), s.get("n_measured"), counts,
                    s.get("median_doppler_residual_hz")),
                 "routine ghost-watch cycle; informational only, "
                 "no action needed")
        if cleared_ghosts:
            named = "; ".join(
                "NORAD %s (%s)" % (k, prev_names.get(k))
                for k in sorted(cleared_ghosts)[:3])
            _log(JOURNAL_SOURCE,
                 "ghost-watch: GHOST_CANDIDATE cleared for %s -- no "
                 "longer a candidate in the latest run" % named,
                 "ghost candidate cleared; informational only, "
                 "no action needed")
        stale_entries = uniq_stale if baseline else new_stale
        if stale_entries:
            def _age_txt(r):
                a = (r.get("details") or {}).get("tle_age_hours")
                return ("%s h" % a) if a is not None else "unknown"

            named = "; ".join(
                "NORAD %s (%s) residual %s Hz, TLE age %s"
                % (r.get("norad_id"), r.get("name"),
                   (r.get("details") or {}).get("doppler_residual_hz"),
                   _age_txt(r))
                for r in stale_entries[:3])
            _log(JOURNAL_SOURCE,
                 "ghost-watch: %d verdict(s) labeled STALE_TLE (not "
                 "ghosts) -- TLE older than 72 h: %s"
                 % (len(stale_entries), named),
                 "candidate-grade signals downgraded by stale TLE data; "
                 "action: refresh the TLE catalog and re-check these "
                 "objects")
        if recovered:
            named = "; ".join(
                "NORAD %s (%s)" % (k, prev_names.get(k))
                for k in sorted(recovered)[:3])
            _log(JOURNAL_SOURCE,
                 "ghost-watch: STALE_TLE recovered for %s -- fresh "
                 "TLE or no longer candidate-grade in the latest run"
                 % named,
                 "stale-TLE condition cleared; informational only, "
                 "no action needed")
        _journal_state_save(_state_path, run, cur_verdicts,
                            cur_names, cur_stale_ages)
    except Exception:
        pass


def _persist_run(run):
    """Persist one run's corrected per-measurement verdicts to the
    durable observation catalog (observations.db, via log_observation).

    Before this wiring the watch loop wrote only ghost_verdicts.jsonl;
    the catalog was fed solely by manual log_observation.py runs, so
    effectively every automated measurement evaporated at process exit
    (147 runs / ~226k analyzed rows vs 15 catalog rows). log_results is
    idempotent on (timestamp, norad_id, svid), so overlapping epoch
    windows and re-runs never duplicate rows.

    do_enrich=False: the automated path makes no SatNOGS network calls
    (keeps the 15-min loop hermetic); first-seen satellites are
    cataloged without enrichment and can be enriched later via
    log_observation.py --backfill.

    Best-effort by contract (same as _journal_run): a catalog failure
    must never break the watch loop. Returns inserted count or None.
    """
    try:
        from log_observation import log_results, DEFAULT_DB
        stats = {}
        n = 0
        for attempt in range(3):
            try:
                n = log_results(
                    {"results": run.get("corrected_verdicts") or []},
                    {}, DEFAULT_DB, run.get("run_utc"),
                    do_enrich=False, stats=stats)
                break
            except Exception:
                if attempt == 2:
                    raise
                time.sleep(2 * (attempt + 1))
        print(f"ghost_watch: persisted {n} observations to catalog "
              f"({stats.get('skipped', 0)} duplicates skipped)")
        return n
    except Exception as e:
        print(f"ghost_watch: WARN: catalog persist failed: {e}",
              file=sys.stderr)
        return None


def main(argv):
    n_epochs = 60
    if "--epochs" in argv:
        n_epochs = int(argv[argv.index("--epochs") + 1])
    from gnss_doppler import analyze, prr_to_doppler_hz, \
        CONSTELLATION_L1_HZ, C
    tmpdir = tempfile.mkdtemp(prefix="ghost_watch_")
    # Each run pulls a ~200 MB DB copy here; it was never removed (90+ copies filled the
    # /tmp quota, 2026-10-11). The unit's ExecStartPre sweep stays as a backstop.
    atexit.register(shutil.rmtree, tmpdir, ignore_errors=True)
    try:
        db_path = pull_latest_db(tmpdir)
    except RuntimeError as e:
        print(f"ghost_watch: ERROR: {e}", file=sys.stderr)
        return 1
    meas = load_measurements(db_path, n_epochs)
    if not meas:
        print("ghost_watch: ERROR: no measurements in DB", file=sys.stderr)
        return 1

    def median_abs_residual(result):
        vals = [abs(r["details"]["doppler_residual_hz"]) for r in result["results"]
                if "doppler_residual_hz" in r.get("details", {})]
        if not vals:
            return float("inf")
        vals.sort()
        n = len(vals)
        return vals[n // 2] if n % 2 else (vals[n // 2 - 1] + vals[n // 2]) / 2

    def sign_meas(sign):
        out = []
        for m in meas:
            freq = m.get("carrier_freq_hz") or \
                CONSTELLATION_L1_HZ.get(m["constellation"])
            if not freq:
                continue
            # sign=+1: stock convention (observed = -prr*f/C).
            # sign=-1: flipped (module documents SIGN_FLIP as field unknown).
            dop = sign * prr_to_doppler_hz(m["prr_m_s"], freq)
            out.append(dict(m, prr_m_s=(-dop * C / freq)))
        return out

    # Sign auto-detect: the correct PRR->Doppler convention is the one
    # that minimizes residuals against SGP4 predictions.
    trials = {}
    for sign in (1, -1):
        res = analyze(sign_meas(sign), OBS_LAT, OBS_LON, OBS_ALT_M)
        trials[sign] = (res, median_abs_residual(res))
    best_sign = min(trials, key=lambda s: trials[s][1])
    raw, _ = trials[best_sign]
    print(f"ghost_watch: sign auto-detect: s=+1 -> "
          f"{trials[1][1]:.0f} Hz median|res|, s=-1 -> "
          f"{trials[-1][1]:.0f} Hz median|res|; using s={best_sign:+d}")

    # Clock correction: compare.py stores |residual|, so the signed median
    # (the actual clock bias) must be reconstructed from observed-predicted.
    signed = [r["details"]["observed_doppler_hz"] -
              r["details"]["predicted_doppler_hz"] for r in raw["results"]
              if "observed_doppler_hz" in r.get("details", {}) and
              "predicted_doppler_hz" in r.get("details", {})]
    signed.sort()
    clock_bias_hz = (signed[len(signed) // 2] if signed else 0.0)
    base = sign_meas(best_sign)
    corrected_meas = []
    for m in base:
        freq = m.get("carrier_freq_hz") or \
            CONSTELLATION_L1_HZ.get(m["constellation"])
        dop = prr_to_doppler_hz(m["prr_m_s"], freq) - clock_bias_hz
        corrected_meas.append(dict(m, prr_m_s=(-dop * C / freq)))
    corr = analyze(corrected_meas, OBS_LAT, OBS_LON, OBS_ALT_M)

    run = {"run_utc": datetime.now(timezone.utc).isoformat(),
           "n_epochs_requested": n_epochs,
           "n_measurements": len(meas),
           "sign_used": best_sign,
           "sign_trial_median_abs_res": {str(s): round(trials[s][1], 1)
                                         for s in trials},
           "clock_bias_correction_hz": round(clock_bias_hz, 1),
           "raw_summary": raw["summary"],
           "corrected_summary": corr["summary"],
           "corrected_verdicts": corr["results"]}
    os.makedirs(OUT_DIR, exist_ok=True)
    with open(VERDICTS_LOG, "a") as f:
        f.write(json.dumps(run) + "\n")

    for label, res in (("sign-corrected", raw), ("+clock-corrected", corr)):
        s = res["summary"]
        print(f"ghost_watch [{label}]: {s['n_analyzed']} analyzed, "
              f"verdicts={json.dumps(s['verdict_counts'])}")
    print(f"  clock-bias correction applied: {clock_bias_hz:.0f} Hz")
    ghosts = [r for r in corr["results"]
              if r.get("verdict") == "GHOST_CANDIDATE"]
    for g in ghosts:
        meta = g.get("_meta", {})
        print(f"  ALERT GHOST_CANDIDATE (post-correction): "
              f"NORAD {g['norad_id']} ({g.get('name')}) "
              f"svid={meta.get('svid')} {meta.get('constellation')} "
              f"residual={g.get('details', {}).get('doppler_residual_hz')} Hz")
    if not ghosts:
        print("  no surviving ghost candidates after corrections")
    print(f"  log: {VERDICTS_LOG}")
    _persist_run(run)
    _journal_run(run, ghosts)
    return 2 if ghosts else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
