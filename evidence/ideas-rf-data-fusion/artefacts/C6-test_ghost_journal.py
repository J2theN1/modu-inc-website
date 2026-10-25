#!/usr/bin/env python3
"""Tests for ghost_watch._journal_run (serendipity journal wiring).

Injects a fake journal logger -- no real journal writes, no P9 access.
Each test gets a fresh journal-state path (tempfile dir), so the
change-only gate sees the baseline/transition sequence the test
intends. Run: python3 -m pytest test_ghost_journal.py
(or plain python3).
"""
import json
import os
import sys
import tempfile

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import ghost_watch  # noqa: E402


def _fresh_state():
    return os.path.join(tempfile.mkdtemp(prefix="gw-journal-state-"),
                        "state.json")


def _run(n_ghosts=0, n_stale=0, stale_age=77.0):
    results = []
    for _ in range(n_stale):
        results.append({"norad_id": 26113, "name": "IMAGE",
                        "verdict": "STALE_TLE",
                        "details": {"doppler_residual_hz": 6100.0,
                                    "tle_age_hours": stale_age,
                                    "epoch_count": 60},
                        "_meta": {"svid": 11, "constellation": "GPS"}})
    ghosts = []
    for _ in range(n_ghosts):
        g = {"norad_id": 90083, "name": "UNKNOWN",
             "verdict": "GHOST_CANDIDATE",
             "details": {"doppler_residual_hz": 6200.0,
                         "tle_age_hours": 10.0, "epoch_count": 60},
             "_meta": {"svid": 99, "constellation": "GPS"}}
        ghosts.append(g)
        results.append(g)
    summary = {"n_analyzed": 1976, "n_measured": 2154,
               "median_doppler_residual_hz": 14.9,
               "verdict_counts": {"CONSISTENT": 1770, "LOW_ELEVATION": 185,
                                  "STALE_TLE": n_stale,
                                  "GHOST_CANDIDATE": n_ghosts}}
    return {"run_utc": "2026-10-12T00:00:00+00:00",
            "corrected_summary": summary,
            "corrected_verdicts": results}, ghosts


class FakeLog:
    def __init__(self):
        self.entries = []

    def __call__(self, source, observation, why_notable=""):
        self.entries.append((source, observation, why_notable))
        return True


def test_routine_run_is_low_signal():
    # First run ever (no baseline): the routine baseline entry is
    # journaled once, worded as plainly informational.
    run, ghosts = _run()
    log = FakeLog()
    ghost_watch._journal_run(run, ghosts, _log=log,
                             _state_path=_fresh_state())
    assert len(log.entries) == 1
    src, obs, why = log.entries[0]
    assert src == "ghost-watch"
    assert "no surviving ghost candidates" in obs
    assert "GHOST_CANDIDATE survived" not in obs
    assert "informational only" in why


def test_ghost_run_is_high_signal_and_stale_labeled():
    run, ghosts = _run(n_ghosts=1, n_stale=1)
    log = FakeLog()
    ghost_watch._journal_run(run, ghosts, _log=log,
                             _state_path=_fresh_state())
    texts = [o for _, o, _ in log.entries]
    ghost_entries = [t for t in texts if "GHOST_CANDIDATE survived" in t]
    stale_entries = [t for t in texts if "labeled STALE_TLE" in t]
    assert len(ghost_entries) == 1 and "90083" in ghost_entries[0]
    assert len(stale_entries) == 1
    # a stale-TLE object must never be labeled a ghost candidate
    assert "GHOST_CANDIDATE" not in stale_entries[0]
    # no routine entry when ghosts present (ghost entries carry totals)
    assert not any("no surviving ghost candidates" in t for t in texts)


def test_dedupes_repeated_objects():
    # Results are per-measurement rows: the same object repeats.
    run, ghosts = _run(n_ghosts=1, n_stale=1)
    dup_ghost = dict(ghosts[0])
    dup_ghost["details"] = dict(ghosts[0]["details"],
                                doppler_residual_hz=9999.0)
    ghosts.append(dup_ghost)
    run["corrected_verdicts"].append(dup_ghost)
    run["corrected_verdicts"].append(run["corrected_verdicts"][0])
    log = FakeLog()
    ghost_watch._journal_run(run, ghosts, _log=log,
                             _state_path=_fresh_state())
    texts = [o for _, o, _ in log.entries]
    ghost_entries = [t for t in texts if "GHOST_CANDIDATE survived" in t]
    stale_entries = [t for t in texts if "labeled STALE_TLE" in t]
    assert len(ghost_entries) == 1 and "9999.0" in ghost_entries[0]
    assert len(stale_entries) == 1
    assert stale_entries[0].count("NORAD 26113") == 1


def test_journal_failure_never_raises():
    def boom(*a, **k):
        raise RuntimeError("journal down")
    run, ghosts = _run(n_ghosts=1)
    ghost_watch._journal_run(run, ghosts, _log=boom,
                             _state_path=_fresh_state())  # must not raise


# --- Change-only gate (Oct 12 harvest-audit fix) ---

def test_first_run_baseline_journals_once():
    sp = _fresh_state()
    run, ghosts = _run()
    log = FakeLog()
    ghost_watch._journal_run(run, ghosts, _log=log, _state_path=sp)
    assert len(log.entries) == 1
    state = json.load(open(sp))
    assert state["verdicts"] == {}


def test_identical_consecutive_runs_journal_nothing():
    sp = _fresh_state()
    log = FakeLog()
    run, ghosts = _run()
    ghost_watch._journal_run(run, ghosts, _log=log, _state_path=sp)
    ghost_watch._journal_run(run, ghosts, _log=log, _state_path=sp)
    assert len(log.entries) == 1  # baseline only; repeat is silent
    run, ghosts = _run(n_ghosts=1, n_stale=1)
    ghost_watch._journal_run(run, ghosts, _log=log, _state_path=sp)
    n = len(log.entries)
    assert n > 1  # the transition journaled
    ghost_watch._journal_run(run, ghosts, _log=log, _state_path=sp)
    assert len(log.entries) == n  # identical repeat: nothing new


def test_new_stale_transition_journals():
    sp = _fresh_state()
    log = FakeLog()
    run, ghosts = _run()
    ghost_watch._journal_run(run, ghosts, _log=log, _state_path=sp)
    assert len(log.entries) == 1
    run, ghosts = _run(n_stale=1)
    ghost_watch._journal_run(run, ghosts, _log=log, _state_path=sp)
    assert len(log.entries) == 2
    _, obs, _ = log.entries[-1]
    assert "labeled STALE_TLE" in obs and "26113" in obs
    # the transition entry is the stale action entry, not a routine one
    assert "no surviving ghost candidates" not in obs


def test_stale_recovery_journals():
    sp = _fresh_state()
    log = FakeLog()
    run, ghosts = _run(n_stale=1)
    ghost_watch._journal_run(run, ghosts, _log=log, _state_path=sp)
    n = len(log.entries)
    run, ghosts = _run()
    ghost_watch._journal_run(run, ghosts, _log=log, _state_path=sp)
    assert len(log.entries) == n + 1
    _, obs, why = log.entries[-1]
    assert "STALE_TLE recovered" in obs and "26113" in obs
    assert "informational only" in why


def test_new_ghost_candidate_journals():
    sp = _fresh_state()
    log = FakeLog()
    run, ghosts = _run()
    ghost_watch._journal_run(run, ghosts, _log=log, _state_path=sp)
    run, ghosts = _run(n_ghosts=1)
    ghost_watch._journal_run(run, ghosts, _log=log, _state_path=sp)
    texts = [o for _, o, _ in log.entries]
    ghost_entries = [t for t in texts if "GHOST_CANDIDATE survived" in t]
    assert len(ghost_entries) == 1 and "90083" in ghost_entries[0]


def test_ghost_candidate_clearing_journals():
    sp = _fresh_state()
    log = FakeLog()
    run, ghosts = _run(n_ghosts=1)
    ghost_watch._journal_run(run, ghosts, _log=log, _state_path=sp)
    n = len(log.entries)
    run, ghosts = _run()
    ghost_watch._journal_run(run, ghosts, _log=log, _state_path=sp)
    assert len(log.entries) == n + 1
    _, obs, why = log.entries[-1]
    assert "GHOST_CANDIDATE cleared" in obs and "90083" in obs
    assert "informational only" in why


def test_stale_age_band_crossing_rejournals_once():
    sp = _fresh_state()
    log = FakeLog()
    run, ghosts = _run(n_stale=1, stale_age=100.0)
    ghost_watch._journal_run(run, ghosts, _log=log, _state_path=sp)
    n = len(log.entries)
    # Same band (100h and 150h are both < 168h): silent.
    run, ghosts = _run(n_stale=1, stale_age=150.0)
    ghost_watch._journal_run(run, ghosts, _log=log, _state_path=sp)
    assert len(log.entries) == n
    # Crossing into the next weekly band: one more STALE_TLE entry.
    run, ghosts = _run(n_stale=1, stale_age=200.0)
    ghost_watch._journal_run(run, ghosts, _log=log, _state_path=sp)
    assert len(log.entries) == n + 1
    assert "labeled STALE_TLE" in log.entries[-1][1]


if __name__ == "__main__":
    test_routine_run_is_low_signal()
    test_ghost_run_is_high_signal_and_stale_labeled()
    test_dedupes_repeated_objects()
    test_journal_failure_never_raises()
    test_first_run_baseline_journals_once()
    test_identical_consecutive_runs_journal_nothing()
    test_new_stale_transition_journals()
    test_stale_recovery_journals()
    test_new_ghost_candidate_journals()
    test_ghost_candidate_clearing_journals()
    test_stale_age_band_crossing_rejournals_once()
    print("test_ghost_journal: 11 passed")
