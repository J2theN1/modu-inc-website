# 34 — Vault X5 fix verification: the Oct 12 record, retained (2026-10-17)

> **Row references:** lettered rows in this pack are per-index and collide across indexes — cite index-exact ("vault X5", "file `29` §1"), never bare; the map is file `28`.

**What this is:** the retained artefact that gap **G-9** in file `30`'s register requires — the Oct 12 fix-verification record behind vault X5's corrected retrieval range (**0.39–0.46**) and "ranked first on every query" (3/3), recovered and placed on file Sat Oct 17 so that Oct 22 Step 6 executes X5's closure from a known state. **Status: RETAINED.** The record the values live in was found (§2); no raw run output survives anywhere (§4) — a well-evidenced absence that closes the hunt permanently. Classification under file `29`'s v2 rules is stated at §5; Oct 22's instructions under each branch are at §6. Nothing in this file is published; publication is Oct 22 Step 5's act. `~/memory` files are quoted and cited only, never edited.

---

## 1. The claim as recorded — and what it does not contain

The values' previously known home, verbatim from `~/memory/2026-10-12.md` (lines 143–147; the day-log as read 2026-10-17, SHA-256 `4f3452f173e6824fd1cab411387213d3ded084f2f5f8d8a09df85cf0fd90abb0`):

> - [event|high] P10 app rebuild completed (Oct 12): the real tokenizer is in and semantic search is verified — 'What are Modu cheat codes?' now returns the cheat codes doc, before it returned F-DPO. This supersedes the earlier in-window state where the rebuild was merely dispatched and still running.
>   - claim: b7870fa33ea64631bd644e808019dce0
>   - quote: "P10 fixed. Real tokenizer in, semantic search verified. "What are Modu cheat codes?" now returns the cheat codes doc. Before it returned F-DPO."
>   - sources: message:assistant-msg-0f569dc6-0b17-f8c9-b776-4d656778cd5b

The claim, its quote, and its cited source all assert the fix and the cheat-codes behaviour change — **none of them contains any of the three values**. The cited source (the parent agent's relay message, 2026-10-12T07:48:51.440Z, retrieved from the runtime message store 2026-10-17) reads in full: "**P10 fixed.** Real tokenizer in, semantic search verified. "What are Modu cheat codes?" now returns the cheat codes doc. Before it returned F-DPO. **2 workers.**" The claim's pointers, followed in §2–§4: the tokenizer-fix run itself (its executing worker, its completion, its working files), the cheat-codes document's pre/post behaviour, and the run's timestamps (completion 2026-10-12T07:48:49Z).

## 2. The run's own record — recovered (the measurement's primary record)

The executing worker's completion report, preserved verbatim in the runtime message store, retrieved 2026-10-17:

- **Record A (handoff form):** message `subagent-progress:6716b135-223b-4c66-8d9d-a9fa83461cd7:completion:834b2752-f8b4-4c42-9bfb-3e1f75f96ed0`, created **2026-10-12T07:48:49.919Z** — the coordinator-completion handoff carrying worker `834b2752-f8b4-4c42-9bfb-3e1f75f96ed0`'s final report (worker_completed_at 2026-10-12T07:48:49Z).
- **Record B (standalone form):** message `assistant-msg-cc3c8c4b-0c3c-4db3-85c3-af8429e04581`, created **2026-10-12T07:48:49.202Z** — the same report body stored on its own. The two records' report text is identical.

The report (§§2, 4, 5 and Key files, quoted verbatim; spelling as written):

> **2. Tokenizer replaced:**
> - Reverse-engineered the real SentencePiece BPE algorithm for EmbeddingGemma-300M (BPE, vocab 262144, byte-fallback, space→▁)
> - Implemented `SentencePieceTokenizer` in pure Java (no native deps)
> - **Differential-tested: Java output is byte-identical to the reference Python `sentencepiece` on 1125 diverse test cases** (plus 4600+ during development)
> - Vocab bundled as 4.4MB binary asset (`assets/sp_vocab.bin`)
> - Patched `MainActivity$onCreate$1$emb$1.smali` to construct `SentencePieceTokenizer(context)` instead of `PlaceholderTokenizer`
>
> **4. Corpus re-ingested** with the real tokenizer (8 docs → `/data/data/ca.modu.sovereignnode/databases/sovereign_corpus.db`)
>
> **5. Test results — "What are Modu cheat codes?":**
> | Query | Top hit | Score |
> |-------|---------|-------|
> | "What are Modu cheat codes?" | **cheat-codes** (Modu Cheat Codes) | 0.4216 ✅ |
> | "Tell me about ghost satellite detection" | **ghost-sat** | 0.3919 ✅ |
> | "How does the AI job board work?" | **ai-job-board** | 0.4635 ✅ |
>
> Before the fix, "What are Modu cheat codes?" returned the F-DPO doc (wrong). Now it returns the correct cheat-codes doc with a clear margin.
>
> ### Key files
> - Java tokenizer: `/tmp/spwork/SentencePieceTokenizer.java` (local VM)
> - Signed APK: `/tmp/p10_final.apk` (Legion, 85.8MB)
> - Vocab binary: `/tmp/sptok/sp_vocab.bin` (Legion)
> - New corpus DB: `/tmp/p10ingest/sovereign_corpus_v3.db` (Legion)
>
> ### Caveats
> - End-to-end UI test wasn't automated (no browser/UIA tools available in this environment), but the pipeline is proven: Java tokenizer ≡ reference implementation, and the embedding+retrieval pipeline with that tokenizer returns correct docs.

**Verification of this record against the task's three tests:** (i) **contains the values** — yes: all three cosines, per query, with the expected document named as top hit on each; (ii) **contemporaneous** — yes: written at the run's completion (07:48:49Z, Oct 12), before every other record that carries the values (§3); (iii) **the measurement's own record** — yes, ruled at §5: it is the executing worker's first-person completion record of the run, not a later summary of one; no other output of the run exists or is pointed to (§4).

## 3. Every other record carrying the values — verified one by one

| Record | Date | Contains 0.4216 / 0.3919 / 0.4635? | Nature |
|---|---|---|---|
| Worker completion report (§2) | 2026-10-12T07:48:49Z | **Yes** — results table | The run's own record (primary) |
| Slice-1 README — `phone-field-platform` (Legion), branch `wren/p10-analyst-slice1-20261012` @ `fbdbf4cbc89a82905eb8b7fde20a3f9202f3cc18`, `apps/sovereign-node-analyst/README.md` (blob `448d9354b39209b49cb99c6fdc5aa2444888c338`), runbook table rows 1–3 | 2026-10-12T16:20:06-07:00 | **Yes** — all three, as "(verified retrieval 0.4216)" / "(0.3919)" / "(0.4635)" expected top citations | Same-day derivative of the same run, written to brief the later on-device proof. Corroborates the transcription; **not an independent chain** (file `29` tie-break (ii): it re-states, it does not re-derive) |
| EIC Step 1 evidence file, row A3 — `~/workspace/goals/procurement-approval-packet/files/eic-step1-package-20261012/TRL6-EVIDENCE.md` (SHA-256 `b040bf2c3fd7627d8d5962228b9a45bff06222dd10e314193f761dbaf16ed1bb`); the pack's vault copy derives from it | 2026-10-12 (evening) | **Yes** — "cheat-codes **0.4216**, ghost-sat **0.3919**, ai-job-board **0.4635**" | Citation layer over §2; A3 itself states the split — ingest report = "pipeline + corpus," fix verification in the memory log |
| Memory log, EIC-package entry (`~/memory/2026-10-12.md` line 520) | 2026-10-12 | **Yes** — "retrieval top-hits 0.4216/0.3919/0.4635" | Same-day summary inside the same log; derivative of §2 via the package |
| Evidence maps (`~/workspace/draft-factory/trl-evidence-map.md`; pack `vault/artefacts/trl-evidence-map.md`) | Oct 12–14 | **Yes** | Citations of A3 |
| P10 Analyst proof records — `~/workspace/p10-analyst-proof-20261014/ASK-PATH-AUDIT-20261014.md` ("Legion-side retrieval with this exact setup ranked the expected doc top-1 for all 3 proof questions (0.4216 / 0.3919 / 0.4635, per the slice README)"), `PROOF-ATTEMPT-20261014.md` (runbook expectations), `GENERATION-PREMORTEM-20261015.md` ("Legion-side reference scores … on record") | Oct 14–15 | **Yes** | Citations of the README/A3. The Oct 14 on-device re-proof produced **no new scores** (the ask cycle did not complete, per the audit) — no second measurement of these figures exists |
| Ingest report — `~/workspace/p10-corpus/P10_RAG_INGEST_REPORT.md` (SHA-256 `03eccf54da5d48c9bb971c033bc21745053e670a40266db3eb8cc0b30037727c`) | 2026-10-12 | **No** — zero occurrences (grep-verified Oct 17, twice) | The **before** record: PlaceholderTokenizer blocker — paraphrase 0.238 = unrelated 0.238, cheat-codes ranked 3rd on its own query, retrieval "unreliable." Retained as the pre-fix half of the pair; excluded as X5's proof (file `33` §1 E-1) |

**Cross-pointer (2026-10-17, evening):** this same retained report is also the first-person record behind vault row **B5**'s differential-test figure — the 1,125-case result its §2 asserts (quoted in §2 above); see file `31` (G-5 capture manifest, B5) for that row's capture state: no standalone run output found across all layers.

## 4. What the hunt did not find — the absence, with its coverage

**No raw run output survives.** No script stdout, results JSON, or query log carrying the scores exists in any searched location. Every working file the run produced lived in `/tmp` and is gone:

| Pointer (from §2's Key files + the ingest report) | State on 2026-10-17 |
|---|---|
| Legion `/tmp/p10ingest/` — `ingest.py`, `docs2/` (the 8 corpus source docs), `sovereign_corpus_v2.db`, `sovereign_corpus_v3.db` | **Absent** — directory does not exist. (`docs2/` was still present Oct 14 per `PROOF-ATTEMPT-20261014.md`; gone by Oct 17 — /tmp cleared between) |
| Legion `/tmp/p10apk/` (APK analysis), `/tmp/p10_final.apk` (signed fixed APK), `/tmp/sptok/sp_vocab.bin` | **Absent** — all three paths verified missing |
| VM `/tmp/spwork/SentencePieceTokenizer.java` | **Absent** — `/tmp/spwork/` does not exist |

No `sovereign_corpus*.db` survives anywhere under `/home/jason` (find to depth 4) or in `~/workspace` — `~/workspace/p10-corpus/` holds only `build_corpus.py` (the corpus-source builder), the pre-fix ingest report, and an empty `docs/`. The executing worker's on-disk session/tool-output directory does not survive on this VM either (no `~/workspace/agents/` directory for worker `834b2752…`); the message-store records at §2 are the surviving form of its report.

**Coverage of the hunt (2026-10-17):** `~/workspace` full-text search for the exact figures (every citing document enumerated at §3); the memory log read in full context around the claim; the runtime message store (the claim's cited source message + a created-at-bounded search for the values, which surfaced §2's records); the Legion — `/tmp` inventory, `/home/jason/workbench/` including `p10-analyst/`, `/home/jason/Projects/phone-field-platform` (worktree plus `git grep` across **all** refs — the values occur only in the slice README, the analyst citation-format example, and its unit-test fixtures, all citing the same verified result), and home-wide finds for corpus DBs and Oct 11–13 verification/retrieval files. The absence is therefore established across the full estate the run touched: **there is no rawer record to recover, on any branch of any further search.**

## 5. Classification — file `29` v2, applied as written

**Ruling: the recovered record is the measurement's OWN record.** Reasoning, on the rules' own text:

- File `29` §1, CERTIFIED-STYLE limb (b): "a retained artefact that is the primary record of the fact directly shows the claim — … **a measurement's own retained record containing the measured values** …"
- Tie-break (i): "An artefact that *contains* the measured values as its own record can satisfy (b); an artefact that *reports* values whose output is retained elsewhere is one chain."
- §2's record **contains** the values as its own record: it is the executing worker's completion report of the run itself — first-person, written at completion (2026-10-12T07:48:49Z), carrying the per-query results as its own results table. It does not point to output retained elsewhere; per §4, no such output exists. It is not a summary of the measurement by another hand: every later record (§3) derives from it, and the memory-log claim that previously terminated the chain is a third-person extraction of a 164-character relay that does not even contain the values — which is why the chain read SINGLE-SOURCE until this record was recovered. File `29`'s erratum states the governing test — "the class stays SINGLE-SOURCE unless the recovered record is the measurement's own record containing the values" — and the recovered record meets it.

**Resulting classes:**

| Figure / claim | Class | Basis |
|---|---|---|
| Corrected range **0.39–0.46** | **CERTIFIED-STYLE (b)** | §2's record, limb (b) / tie-break (i) |
| **"Ranked first on every query" (3/3)** | **CERTIFIED-STYLE (b)** | The same table shows each proof query's top hit as the expected document |
| Range **as quoted** in MC-1 ("0.42–0.46") | **UNLABELLED** — unchanged | Contradicted by the values themselves (0.3919 < 0.42); the "0.42" low end stays cut in every branch |

**The caveat, printed plainly:** the record is the executing agent's authored completion report, not a machine-generated instrument log, and no raw output survives against which its transcription could be re-checked (§4). The (b) ruling rests on the report being the run's primary record — contemporaneous, first-person, sole carrier of the values — not on a second independent chain (there is none; §3's corroborations are derivatives). **If Oct 22 Step 2's label application prefers the stricter reading — agent prose is a report-*of*, not a record-*of* — then the same artefact publishes and both figures travel SINGLE-SOURCE instead.** The artefact, the publication act, and the quoted figures are identical under both readings; only the printed label differs. This ruling supersedes the presumption in file `30`'s Step 6 X5 row ("the range then travels SINGLE-SOURCE under file `29`'s corrected reading"), which was written before the record was recovered; file `29`'s erratum test governs and is met on the reading stated here. File `29`'s erratum itself stands unedited — it was true of the record as then known.

## 6. Oct 22 Step 6 — what the day now does with X5

**Planned branch — RETAIN + PUBLISH (executes by default):**

1. **Step 5:** copy this file (`34`) into `evidence-page/artefacts/` and link it from the page's index as vault X5's proof artefact, flipping the E-1 slot from PENDING to held. The ingest report is **not** published as X5's proof under any branch (file `33` §1 E-1 stands).
2. **Step 2 (label application, in the build record):** record the corrected range and ranked-first as **CERTIFIED-STYLE (b)** per §5 — or SINGLE-SOURCE if the stricter reading is preferred; the build record states which was applied and cites this file's §5 either way.
3. **Step 6:** RE-HOME the corrected range **0.39–0.46** and "ranked first on every query" into MC-1, citing the evidence-page URL for this file. The "0.42" low end is cut (vault X5; it proceeds under both branches).

**Fallback branch — DROP (only on a Step 2 rejection of the record):** if the label application rules the completion report not a retainable artefact at all, drop the range from MC-1 under vault X5's stated fallback; ranked-first, resting on the same record, drops with it. **No further hunt is needed or possible under either branch** — §4's coverage is the full estate. The branch decision is a labelling judgement on a record now in hand, not a search outcome, and never a surprise on the day.

---

*Retained 2026-10-17 by Wren, executing register G-9 from file `30`. Sources, all read at source 2026-10-17: `~/memory/2026-10-12.md` lines 143–147 + line 520 (quoted, never edited); runtime message-store records `assistant-msg-0f569dc6-0b17-f8c9-b776-4d656778cd5b`, `assistant-msg-cc3c8c4b-0c3c-4db3-85c3-af8429e04581`, `subagent-progress:6716b135-223b-4c66-8d9d-a9fa83461cd7:completion:834b2752-f8b4-4c42-9bfb-3e1f75f96ed0`; `TRL6-EVIDENCE.md` row A3 (EIC original, hash-verified above); the slice-1 README via `git show` on the Legion (branch tip + blob hashes above); `~/workspace/p10-corpus/P10_RAG_INGEST_REPORT.md` + `build_corpus.py` (read in full); the Oct 14–15 P10 Analyst records; file `33` §1 E-1 + addendum; file `29` §1 (rules v2) + the X5/B6 erratum; file `30` register G-9 + Step 6 X5 row. No file edited except file `30`'s G-9 line (dated pointer, per the register's own convention) and the ops board.*
