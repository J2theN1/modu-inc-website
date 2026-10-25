# P9 Own Models — inventory + LIVE generation test

Sat Oct 24, 2026, ~10:42–11:05 PDT. Lane: P9 ENRICHMENT + OWN-MODELS.
Jason's word (10:35 PDT): dig through the estate's own-models work and
enrich; Gemini is expected not to work on the unlocked phone — our own
models are the path. Device acts on Jason's P9 only, serial-verified
before anything else. Fences held: no broker SETs, no flashing, PhoneLab
never touched.

---

## 1. Identity gate (before any device act)

```
ro.serialno   = 49251FDAQ000KV      ← matches Jason's P9 exactly
ro.product.model = Pixel 9
ro.build.id   = CP3A.261005.005     ← current post-OTA build (agrees E1)
```

Route: Legion lane → LAN 192.168.1.91 → adb 192.168.1.91:5555 (the
Tailnet path does not answer, per E1).

---

## 2. Inventory — our own models and their serving stack

### 2.1 Estate source

| Asset | Estate location |
|---|---|
| ai_worker source (job daemon) | `~/workspace/goals/p9-ai-hardware-tpu-aicore-below-hal/hidden_files/ai_worker.py` (401 lines) + boot/watchdog launcher `modu-ai-worker.sh` |
| LLM model registry | same dir, `models-spark-default.json` (roles, paths, backends, measured notes) |
| embed_server health/protocol record | same dir, `embed-server-20261009.md` |
| Oct 10 knowledge test (Qwen 0.6B live) | same dir, `ai-worker-test-20261010.md` |
| On-device copies | `/data/local/tmp/ai_worker/ai_worker.py` (27,234 B — **newer than the estate copy**: its generate path routes via an HTTP wrapper on :8794; the estate copy spawns GemmaBench2 directly) |

### 2.2 On-device model assets (verified live, Oct 24)

`/data/local/tmp/gemmabench/`:

| File | Bytes | Model | Registry notes |
|---|---|---|---|
| `qwen06b.litertlm` | 344,671,744 | **Qwen3-0.6B int4** | GPU backend; fastest init (~5.1 s); ai_worker's generate model |
| `spark17b_int4.litertlm` | 1,263,128,496 | **iFlytek Spark-X2.5-1.7B int4** (reasoning) | GPU; TTFT ~0.9 s; registry default for most roles — but ai_worker does not pin it (Oct 10 flip-flop finding stands) |
| `ministral3b.litertlm` | 2,342,866,928 | **Ministral-3-3B-Instruct int4** | GPU, full delegation; 5.91 tok/s, ~45 s cold init — **present on the P9 itself**, not only proven on the P10 |
| `model.litertlm` | 285,577,392 | (Gemma-class bench model; bench logs present) | — |
| `bench.dex`, `bench3.dex`, `apk/classes*.dex`, `lib/` | — | GemmaBench2 harness | the one-shot CLI path |

Compiled-model caches (`*_mldrift_*_cache.bin`, XNNPACK caches) exist for
all three LLMs — the GPU path has run on this device, most recently
**Oct 22 01:38** (qwen06b caches rebuilt during the root-restore window).

`/data/local/tmp/tflite_test/` (embed stack):

| File | Bytes | Note |
|---|---|---|
| `embed_server` (+ `.batch`, `.pool`, `.single-20261010`, `.old-20261010` variants) | 85,856 (current) | NDK binary, TF Lite + NNAPI delegate. **Current binary differs from the 66,360 B build in the Oct 9 record** — it was rebuilt Oct 10 03:20 |
| `model_fixed2.tflite` | 10,805,416 | MiniLM-L6 int8 — the proven production embed model |
| `model.tflite`, `model_fixed.tflite` | 11,302,288 each | MiniLM variants |
| `model_int16x8.tflite` | 11,594,456 | int16x8 variant, unused per Oct 9 record |

`/data/local/tmp/llm_server/`: `llm_server.dex`, `start.sh`, `models.json`
(+ logs) — the persistent LiteRT-LM server behind the :8794 wrapper.

### 2.3 Serving stack state on arrival (Oct 24, ~10:42)

| Component | Port | State on arrival |
|---|---|---|
| embed_server (MiniLM → Edge TPU) | 127.0.0.1:8788 | **LISTENING** (pid 9972) — agrees E1 |
| llm_server (LiteRT-LM) | 127.0.0.1:8791 | **LISTENING** — E1 did not inventory this port |
| LLM HTTP wrapper | 127.0.0.1:8794 | LISTENING (found during the test) |
| **ai_worker (job daemon)** | 127.0.0.1:8790 | **DOWN** — dir, source, token, embed_bundle all present; pidfile stale (pid 3580, dead); worker.log's last start was Oct 22 01:25 and every Oct start logged "embed warmup failed: Connection refused" (embed_server was down in those windows) |
| rag_server (P9-knowledge RAG) | 127.0.0.1:8789 | DOWN — so `rag_search` jobs currently fail; retrieval corpus is `/data/local/tmp/p9-knowledge/` per the Oct 10 record |

This refines E1's correction #3: ai_worker is "present, daemon down,
embed backend up" — and additionally its **LLM server + wrapper were
already up**; only the job-daemon layer and the RAG layer were down.

---

## 3. LIVE TEST — one real generation from our own model

### 3.1 Method

1. Started ai_worker the documented way its watchdog does (Termux
   python3, `AI_WORKER_DIR=/data/local/tmp/ai_worker`, detached,
   appending to the existing `worker.log`). Start time 10:49:39 PDT.
   Log: `listening 127.0.0.1:8790` → `wordpiece embedder ready` →
   **`embed warmup done`** — the first recorded start where the TPU
   warmup succeeded (embed_server was up this time).
2. Corrected the stale pidfile to the real worker pid (**31312**) so the
   boot watchdog's liveness check stays truthful.
3. Ran an on-device test script (Termux python3, stdlib only) that read
   the API token from `/data/local/tmp/ai_worker/.token` **on the
   device** (the token never left the P9), then:
   `GET /health` → `POST /job {type:"generate"}` → poll → one
   `POST /job {type:"embed"}` as a TPU-path companion check.

### 3.2 Health (verbatim)

```json
{"ok": true, "uptime_s": 113.4, "backends": {"embed": true, "rag_search": false, "generate": true}, "queues": {"tpu": 0, "gpu": 0}, "jobs": {}}
```

### 3.3 The generation (verbatim)

- **Prompt:** `Answer in one short sentence: what is the capital of France?`
- **Job:** `job-6764c3eda6d3`, queue `gpu`, status **done** at first poll (5 s)
- **Output text, exactly as returned:**

```

Paris.
```

(the result `text` field is `"\n\nParis."` — two leading newlines, then
the answer; nothing else)

- **Result record (verbatim):**
  `{"text": "\n\nParis.", "total_ms": 4670, "backend": "http-8794", "model": "qwen06b", "note": "via :8794"}`; worker-side total 4,690.5 ms.

### 3.4 Which backend executed it (from logs, stated precisely)

Chain: ai_worker (:8790) → LLM HTTP wrapper (:8794) → **llm_server
(:8791, LiteRT-LM)** → `qwen06b.litertlm` (Qwen3-0.6B int4,
`/data/local/tmp/gemmabench/qwen06b.litertlm`).
The registry configures qwen06b on the **Mali-G715 GPU** (OpenCL/mldrift)
backend, and this device's llm_server log shows the LiteRT-LM
compiled-model executor active (`llm_litert_compiled_model_executor`),
with one honest caveat: the log line `OpenCL sampler not available,
falling back to statically linked C API` shows the **sampler** step fell
back to CPU in the server process — the model executor itself is the
LiteRT compiled-model path. I did not take a per-op GPU trace of this
specific run, and I am not claiming one. Historical GPU bench receipts
for this exact model on this device: `bench2_qwen_gpu.log` (Oct 10) and
the Oct 10 test's 14–16 tok/s through ai_worker.

### 3.5 Companion check — the TPU path through the same worker (verbatim)

- **Job:** `embed`, text `satellite pass prediction for the ISS`
- **Result:** status done, **dim 384**, backend **`edgetpu`**, model
  `minilm-l6-int8`, **93.4 ms** end-to-end through the worker (on-device
  WordPiece tokenization included — the Oct 9 design needed PC-side
  tokenization; the current worker build embeds on-device).
- Embedding head (first 5 of 384 floats):
  `[-0.02243100106716156, -0.02833390422165394, -0.00826405081897974, -0.03777850419282913, 0.03541730344295502]`

So in one session, on the current post-OTA build: **generation on our
own Qwen (GPU path) and embeddings on our own MiniLM (Edge TPU) both
executed live through Jason's own job daemon.** Gemini/AICore was not
involved in either.

---

## 4. What does not work right now (exact blockers, with evidence)

1. **rag_search: down.** Health reports `rag_search: false`; :8789 is
   not listening. The worker's RAG job type will error until rag_server
   is started (its corpus `/data/local/tmp/p9-knowledge/`, 1,363 records
   post-cutover per Oct 10). Not started in this lane — generation was
   the brief; flagged here as the one-command follow-up.
2. **Model selection is still not pinned.** ai_worker serves
   `qwen06b`; the registry wants `spark17b` as default for most roles
   and records the Oct 10 flip-flop (health claiming spark17b while
   qwen06b served). Today's run again served qwen06b. Spark remains a
   llm_server-side `use_model` away, unproven through the worker.
3. **ai_worker does not auto-start reliably.** It was down on arrival
   despite the Magisk service.d watchdog design (the watchdog subshell
   does not survive whatever killed the Oct 22 instance; pidfile was
   stale). It is up now (pid 31312) but a reboot may or may not restore
   it — unproven either way; today's start is not evidence about boot.

---

## 5. What this means for the plan's jobs

- **J1 (TPU triage of satellite captures):** the *substrate is live*.
  The embed job type executed on the Edge TPU today through the
  production worker; embed_server is a proven template for a
  classifier server (same NNAPI-delegate shape). What J1 still needs is
  purely the model side: the YAMNet-class int8 classifier compiled via
  I3 (Legion-side quantisation) and served the same way. No new
  plumbing, no new daemon work.
- **J2 (GNSS/sensor anomaly pre-scoring):** generation substrate live
  (Qwen 0.6B via the worker) for on-device scoring narration/summaries,
  embeddings live for feature-side similarity, and Part A's enrichment
  shows the input data is richer than planned (54 sats/epoch root
  binder GNSS, CHRE/USF on-device fusion, IPowerStats/IThermal
  context). What J2 still needs is the scoring model itself (the
  engineered-features MLP/TCN or the rules baseline) — a build, as the
  plan already prices it. Nothing about the runtime is blocking it.
- **J4 (Sovereign Node edge-inference proof bench):** **can be assembled
  today from receipted pieces** — own-model generation (this report,
  verbatim output + timings) + TPU embeddings (this report + Oct
  benchmarks) + the plan's capture corpora. The plan's J4 wording
  ("AICore generate() + one TPU-native model") should be corrected:
  the AICore leg is the blocked one (specs annex §2.4/§5.5); the
  own-model generation leg is the live substitute and is arguably the
  better Sovereign Node story — it depends on no Google entitlement.
- **J3 (Nano summariser):** unaffected — still parked, now with a
  working own-model summariser substrate available if the consumer ever
  wants the summary without Nano (Qwen 0.6B is the registry's own
  `summarizer` role choice).

---

## 6. Lane notes

- Legion lane was saturated by two sibling lanes for much of this run
  (repeated empty `process.result` reads — the known flap, worse under
  parallel load). All device work used short serial calls + detached
  launches with file polling; every verdict above rests on file
  contents or repeated reads. One ambiguous spawn result was verified
  on-device before proceeding (the start had in fact landed).
- Fences held: serial gate first; no SETs; no flashing; PhoneLab
  untouched (it was not disturbed — no force-stop, no relaunch);
  the only device state changed is ai_worker running again (its own
  documented start path) + its pidfile corrected + one test script at
  `/data/local/tmp/aiw_test.py`.
