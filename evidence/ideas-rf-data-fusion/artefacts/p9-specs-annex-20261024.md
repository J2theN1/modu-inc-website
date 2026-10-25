# P9 Specs Annex — patent / FCC / teardown enrichment

Sat Oct 24, 2026. Compiled estate-first from Jason's own mined records,
checked against `p9-ai-hardware-plan-20261024.md` (the plan) and
`p9-e1-census-20261024.md` (E1, today's verified device state).
Contradictions are flagged, never silently merged — same discipline as E1.

---

## 1. Where the compiled material lives (the repo Jason remembered)

There is no single "pixel9-specs" repo. The mined-and-compiled P9 material
lives in four places, all on the Legion:

| Layer | Path | What it holds |
|---|---|---|
| **Compiled index repo** | `/home/jason/Projects/github/pc-github-index/` | The estate's compiled research repo. P9-relevant: `projects/pixel10-gk2mp-lab/` (patent registry v1–v14, FCC/ISED map, findings waves incl. Pixel 9 waves 7/8, FCC-patent waves 26/27), `docs/phone/` (27 phone programme docs), `docs/operations/device_profiles/pixel9_tokay.json`, `research/bundles/pixel10-gk2mp-regulatory.json` |
| **Station wiki** | `/home/jason/Projects/github/modu-station-wiki/p9-ledger.json` | The P9 ledger (updated 2026-10-09): hardware blocks, 9 mined AOSP HAL families, ai_hardware + tpu_stack sections, powerstats |
| **Phone-mine packs** | `/home/jason/phone-mine/` | Raw mined packs: `aicore_aidl/` (jadx-decompiled AICore AIDL sources), `aicore_apk/`, `aicore_access/`, `ai_api/`, `pixel9/`, `pixel10/`, `classify/` (on-device classification dumps), PhoneLab GNSS/sensor pulls |
| **Goal corpora (VM)** | `~/workspace/goals/p9-ai-hardware-tpu-aicore-below-hal/hidden_files/` and `~/workspace/goals/p9-rf-firmware-bcm4390-modem-thread/hidden_files/` | The Oct 9–11 working records: GXP ABI verification, TPU Ghidra lane, embed-server protocol, firmware takedown audit, chip exploration, AoC blob identification, benchmarks, ai_worker source |

Also found: `/home/jason/workbench/indexes/aicore_teardown/` — a FAISS
semantic index (Jul 25) over the AICore teardown corpus in phone-mine, and
`/home/jason/workbench/claude-selftools/memory-backup-20261009/project_p9_accelerator_firmware_disassembled_20260910.md`
— the Sep 10 accelerator-firmware disassembly record (§3.1).

Searched and ruled out: `/home/jason/phone-hardware-git` (USB-serial
research, not P9 specs), `/home/jason/WIKI` (holds the AICore/Gemma wiki
pages, pointers rather than the compiled corpus).

---

## 2. Load-bearing specs, block by block

Each fact carries its estate source. Verdicts are vs the plan + E1.

### 2.1 Edge TPU (Darwinn, "rio") — the plan understates what is proven

- **Real-model offload is already measured, not hypothetical.** The estate's
  embed_server (Jason-built, Sep 2026) runs MiniLM-L6 int8 under the NNAPI
  `google-edgetpu` delegate: **69/292 nodes delegated in 7 partitions**,
  warmup ~69.5 ms, steady-state **~57 ms TPU inference / ~73 ms end-to-end,
  12.7 req/s sequential, 17.0 req/s at 5-way parallel**, output verified sane
  (384-dim). Sources: ledger `ai_hardware.edgetpu`; `embed-server-20261009.md`
  §1/§3; `p9-ai-benchmark-20261010.md` §1.
- **Node count understates compute offload.** The benchmark record's prior
  analysis puts **~97% of MACs on the TPU** for the same 69/292-node
  partition. Source: `p9-ai-benchmark-20261010.md` §1 config line.
  → E2's ">80% offload" goal is meaningless until it says *which* metric;
  the estate's one measured model is 23.6% by nodes, ~97% by MACs.
- **Firmware identity.** Edge TPU firmware is `edgetpu-rio.fw` (1.1 MB;
  "rio" is this generation's TPU codename). Its real-time management core is
  an **ARM Cortex-R52** running **SafeRTOS**; the image disassembled cleanly
  in Ghidra (1,072 functions). Mailbox architecture recovered from debug
  strings: `IccMailbox<Command,Response>`, `ClientMailboxManager`
  (multi-client virtualized scheduler), `GsocSyncMailbox`. Compiler library
  on the host side: `libedgetpu_tflite_compiler.so` (Darwinn). Sources:
  accelerator-firmware disassembly record (Sep 10, 2026);
  ledger `tpu_stack`.
- **Clocks/TOPS: honest estate negative.** The disassembly pass specifically
  failed to isolate clock/PLL configuration code in the firmware image, and
  no TOPS figure exists anywhere in the estate. The plan's refusal to cite
  a TOPS number is confirmed correct.

### 2.2 GXP / Callisto — the plan's §1.5 verdict is contradicted by the estate

- **The complete /dev/gxp ioctl ABI is public, recovered, and live-verified
  on this P9.** Google publishes the driver source
  (`kernel/google-modules/gxp/zuma`, caimito branches); the estate lane
  extracted the full ABI (44 ioctls, magic 0xEE), cross-checked every code
  against the shipped `gxp.ko`'s dispatch, disassembled
  `/vendor/lib64/libgxp.so` to recover the real session flow, and executed
  the two read-only ioctls live on the device (Oct 10, pre-OTA build).
  Source: `gxp-below-hal-20261009.md` (whole report).
- **Live GET_SPECS on the P9:** **3 cores**, features=0x1 (**MCU mode**),
  max 15 virtual devices / 7 concurrently active, telemetry buffers present.
  Driver interface **v1.33** (build `gfd03489e79aa`) — newer than the newest
  public snapshot (v1.31); one ioctl (`0x4004EE12`, added 1.32/1.33) has no
  public definition and is flagged do-not-call.
- **What the block is:** the 3 Callisto cores are DSP cores
  (`gxp_callisto_fw_core{0,1,2}`, ~299 KB each, Ghidra-analysed: 506
  functions in the Callisto image) running loadable libraries — and the same
  GCIP/GXP driver fronts the **TPU mailbox** (`GXP_MAP_TPU_MBX_QUEUE`,
  `struct edgetpu_mailbox_attr` from `kernel/google-modules/edgetpu`).
  Source: `tpu-ghidra-20261010.md`; accelerator-firmware record;
  `gxp-below-hal-20261009.md` §3/§7.
- **The one missing piece** for below-HAL TPU command submission is the
  48-byte UCI opaque payload format inside
  `struct gxp_mailbox_uci_command_ioctl` (128 B, opaque at offset 48),
  defined by the MCU firmware — a bounded RE target with a built, validated
  capstone analysis pipeline waiting on the blobs
  (`tpu-ghidra-src/analyze_callisto.py`). It is not "no path"; it is one
  struct layout.
- E1 today confirmed the surface on the current build: `/dev/gxp` exists
  (`crw-rw-rw- system:camera 487,0`), `libgxp.so` present — and the estate
  record adds that shell-context `open()` is SELinux-denied despite the 666
  DAC mode; root opens it fine. Source: E1 census table;
  `gxp-below-hal-20261009.md` §2.

### 2.3 Mali GPU compute

- **Mali-G715** confirmed as the generation substrate: ai_worker's own
  `/backends` table lists generate as "Mali-G715 (OpenCL)", LiteRT-LM with
  the GPU (mldrift/OpenCL) delegate; on-device compiled-model caches
  (`*_mldrift_program_cache.bin`, `*_mldrift_weight_cache.bin`) exist for all
  three LLM models. Sources: `ai_worker.py` (estate copy, `/backends`);
  on-device listing Oct 24 (see the own-models report).
- No estate clock/core-count figure for the GPU was found; the plan asserts
  nothing numeric here either. No contradiction.

### 2.4 AICore / Gemini Nano

- E1 (today): AICore `0.release.prod_aicore_20260917.00_RC01`, data dir
  **1.7 MB — no model store**. The ledger's blocker list explains the other
  half: the MediaPipe path's model file
  `/data/local/tmp/llm/gemma3-1b-it.task` is **missing**, and the
  `USE_ON_DEVICE_INTELLIGENCE` / `VENDOR_INTELLIGENCE` permissions are
  signature-level, ungrantable to a debug APK. Sources: E1 census;
  ledger `ai_hardware.aicore`.
- The estate's AICore RE corpus is deeper than the plan credits: jadx
  AIDL sources, the APK, and access probes are mined and indexed
  (`/home/jason/phone-mine/aicore_aidl`, `aicore_apk`, `aicore_access`;
  FAISS index at `/home/jason/workbench/indexes/aicore_teardown/`).
  The plan's §1.4 verdict (sanctioned ML Kit route or nothing; side-door =
  folklore) still stands — but "folklore, mostly" should read "RE'd,
  gated on signature permissions + an absent model payload."

### 2.5 BCM4390 (Wi-Fi / Bluetooth combo)

- Chip: **Broadcom BCM4390**, driver `bcmdhd4390`, control via
  SIOCDEVPRIVATE ioctls — ledger status "controlled". Firmware on-device:
  `fw_bcmdhd.bin_4390_a0/b0/b1` (2.5 MB, never strings-scanned as of the
  Oct 10 audit) plus CLM (regulatory), TX-cap and calibration blobs;
  BT side is a separate `.hcd` in which **no spectral/FFT command exists**
  (verified — stop hunting it). Sources: ledger `hardware_blocks.wifi`;
  `firmware-takedown-audit-20261010.md` target 2 + "not worth" table.
- **A radiotap monitor interface already exists**: `wondertap0`
  (ieee802.11/radiotap, real mac80211 phy binding) sits pre-created and
  DOWN; `wlan1` and `aware_nmi0` (Wi-Fi Aware) also exist. Bringing
  wondertap0 up is a state change and was not done. Source:
  `p9-chip-exploration-20261010.md` §1–2.
- Mined Wi-Fi HAL key finding: `IWifiRttController.enableResponder()`
  makes the P9 an **RTT responder** (P9↔P10 ranging unblocked at HAL);
  TX-power scenario control is SAR-limits only, antenna mode is MIMO
  configuration, not per-antenna selection. Source: ledger
  `mined_aosp_hals.wifi` + `antenna_rf`.

### 2.6 Thread / 802.15.4

- Ledger + E1 agree exactly: kernel stack loaded (mac802154 etc. Live),
  Thread HAL absent from the user build ("userdebug-only", unblock = AOSP
  build), `IThreadChip.aidl` mined from the AOSP tree. Sources: ledger
  `hardware_blocks.thread_802154`, `mined_aosp_hals.threadnetwork`; E1.
- Regulatory layer: the Pixel 9 FCC filing (below) contains a **Thread
  radio report** — the radio is certified at family level; the gap is
  purely the HAL/framework layer, exactly the plan §5.1 class-(a) shape.

### 2.7 Bluetooth Channel Sounding

- Ledger: `IBluetoothChannelSounding` HAL, "CS sec level 1", status
  controlled; E1 today: HAL registered + framework `ranging` service
  present. FCC filing includes **BLE Channel Sounding ASK and GFSK
  reports** for the Pixel 9 — certified test material predates the P10
  work. Sources: ledger `hardware_blocks.bluetooth`; E1;
  gk2mp-lab wave 7.

### 2.8 UWB — resolved negative (layer discipline matters)

- Ledger: chip "Qorvo QM35825", status **absent_hardware**, "vestigial
  driver". Takedown audit: "UWB (QM35) — hardware absent. Kernel drivers
  vestigial. **Stop looking.**" Sources: ledger `hardware_blocks.uwb`;
  `firmware-takedown-audit-20261010.md`.
- Apparent conflict: the Pixel 9 *family* FCC filing contains a UWB
  report (wave 7). Resolution, per the lab's own layer model
  (`DEVICE_BASELINE.md` §Layer model): a filing exhibit certifies a
  configuration of the family (UWB is populated on Pro variants); the
  on-device evidence for **this unit** is unambiguous — no UWB hardware.
  **Verdict: Jason's P9 has no UWB. Do not re-mine this.**

### 2.9 Modem / NTN (Exynos 5400, "Shannon")

- Modem: **Exynos 5400**; `modem.bin` (88 MB) strings yield **2,684 unique
  AT commands** and the full Skylo NTN stack (`+SKYLOTEST`, `+NTNTEST`,
  `+NTNSATCFG`, `+NTNMETRIC`…); ledger records NTN flags all enabled
  (n255/n256). A separate `/vendor/firmware/ntn_modem` blob exists,
  unexamined. Sources: ledger `hardware_blocks.cellular`;
  `firmware-takedown-audit-20261010.md` target 4.
- NTN is plumbed through the Android telephony framework
  (`NtnSignalStrength` visible in `dumpsys telephony.registry`) — satellite
  attach/signal can be monitored with no AT traffic at all. Source:
  `p9-chip-exploration-20261010.md` §4.
- FCC layer: the P9 filing carries an **NTN Band 255 report** and spatial
  TAS (time-averaged SAR) operational descriptions — the transmit-power
  control architecture is documented in the filing, not opaque. Source:
  gk2mp-lab wave 7.

### 2.10 GNSS (BCM4776-class)

- Ledger names **BCM47765**; the takedown audit says BCM4776-class — same
  family, no conflict. HAL fully unlocked via root binder: **54
  sats/epoch** (vs 3 via framework), chip-computed SatellitePvt,
  `pseudorangeRateMps` Doppler, carrier phase, 5-tap correlator vectors.
  Sources: ledger `hardware_blocks.gnss`, `mined_aosp_hals.gnss`;
  `firmware-takedown-audit-20261010.md` target 5.
  → J2's input data is far richer live than the plan's "Jul 25 captures"
  framing suggests.

### 2.11 AoC / always-on sensing (chip codename "polygon")

- AoC firmware `aoc.bin` (29 MB) fully blob-identified: chip codename
  **polygon**; main RTOS image (FreeRTOS + CHRE: **27 nanoapps, 800
  MIPS**); **USF is resolved** — rec00 is the USF sensor-fusion/algorithm
  image (IMU state machine, ST VD6282 sensor, `com.google.sensor.*`
  gestures); audio is the ASP framework (Waves MaxxAudio, LC3, HiFi
  codecs) with **TFLite models embedded in firmware** (hotword-AEC with a
  custom `MusdetOpResolver` op, an UltrasonicProcessor model); speaker amp
  DSP firmware is Cirrus Logic cs35l41. 58 `/dev/acd-*` nodes; audio taps
  are session-gated by design. Sources: `aoc-blob-id-20261010.md`;
  `firmware-takedown-audit-20261010.md` targets 3/6; ledger `powerstats`
  (AoC/FF1/HF1/HF0 power entities live in `dumpsys powerstats`).
- Mined sensor HAL: 42 sensor types, `injectSensorData()` synthetic
  injection exists. Source: ledger `mined_aosp_hals.sensors`.

### 2.12 Power / thermal instrumentation (new to the plan)

- **`IPowerStats.getEnergyConsumed()` is mined and powerstats is
  confirmed live** — per-component energy in microjoules, on-device, no
  external meter. **IThermal is mined**: 20 temperature types including
  TPU/MODEM/WIFI plus `forecastSkinTemperature()`. Sources: ledger
  `mined_aosp_hals.power`/`thermal`, `powerstats`.
  → E2's "energy per inference (battery delta)" and its throttle-curve
  skin-temp sampling both have direct HAL instruments the plan doesn't
  use. Battery-delta is the crude fallback, not the method.

### 2.13 Memory / storage

- E1 (today, authoritative): /data 59% used, **≈45.8 GiB free**; battery
  100%, 28.4 °C idle. The plan's "51 GB free" is the Oct 11 reading —
  drift, already flagged by E1. On-device model storage is dominated by
  `/data/local/tmp/gemmabench/` (~7.8 GB incl. compiled-model caches) —
  see the own-models report inventory.

---

## 3. Teardown corpus — what the disassembly work established

### 3.1 Accelerator firmware (Sep 10, 2026 session)

Source: `/home/jason/workbench/claude-selftools/memory-backup-20261009/project_p9_accelerator_firmware_disassembled_20260910.md`.

- Pulled from the vendor partition: `edgetpu-rio.fw` (1.1 MB),
  `gxp-callisto.fw` (311 KB), and three per-core GXP firmware files —
  **confirming GXP = 3 cores** independently of GET_SPECS.
- Both images disassembled completely in Ghidra as raw ARM32: 1,072
  functions (TPU fw), 506 (GXP fw); standard Cortex-R vector tables;
  internal Google source paths (`third_party/darwinn/...`) recovered from
  strings — the images are not encrypted.
- Mailbox/scheduler class architecture recovered (§2.1). Symbol tables are
  stripped; class/string names lack exact function addresses.
- Honest negatives recorded: clock/PLL MMIO config not isolated; two MMIO
  regions (0x590000, 0xb00000) unidentifiable from this image alone.

### 3.2 Firmware takedown audit (Oct 10, 2026)

Source: `firmware-takedown-audit-20261010.md` (RF goal corpus). Ranked
never-opened firmware: `gxp_callisto_fw_core{0,1,2}` (rank 1 — UCI
vocabulary), `fw_bcmdhd.bin_4390_*` (rank 2), `aoc.bin` (rank 3 — since
identified, §2.11), `ntn_modem` (rank 4). Explicit stop-looking list:
UWB, BT spectral FFT, Titan M2 direct RE.

### 3.3 AICore teardown packs

Source: `/home/jason/phone-mine/` (`aicore_aidl`, `aicore_apk`,
`aicore_access`, `ai_api`) + inventory in
`/home/jason/workbench/reports/claude-handoff-continue-20260726/evidence/phone-teardown-inventory.txt`.
JADX-decompiled AICore AIDL interfaces and the APK are on file and
FAISS-indexed — any future AICore question starts from decompiled
sources, not speculation.

---

## 4. FCC / patent layer (compiled repo findings)

- **Pixel 9 FCC ID: `A4RGR83Y`** — filing contains separate LTE and 5G NR
  reports, antenna reports, SAR material, TAS operational descriptions,
  BLE Channel Sounding ASK/GFSK reports, Thread radio report, Wi-Fi
  6 GHz/VLP reports, NTN Band 255 report, and (family-level) UWB and
  mmWave/Part 30 material for the US configuration. Sources: gk2mp-lab
  findings `2026-07-21-pixel9-control-baseline-wave-7.md`,
  `2026-07-21-hpue-wave-5.md` (fccid.io/A4RGR83Y).
- The lab's FCC map + baseline docs (`RF_FCC_ISED_MAP.md`,
  `DEVICE_BASELINE.md`) are **Pixel 10 (GK2MP, FCC A4RGK2MP, ISED
  10395A-GK2MP)** documents — do not cite their identifiers for the P9.
  Their reusable contribution to the P9 programme is the **10-layer
  capability model** (spec → silicon → populated → antenna → certified →
  firmware-enabled → provisioned → HAL-exposed → API → observed), which
  is exactly the discipline that resolves the UWB case in §2.8.
- Patent registry (`patents/patent-registry-v1…v14`, canonical v14):
  a scored, evidence-labelled family registry built around the Pixel 10
  with the Pixel 9 as control baseline. Canonical v14 carries 6 families
  (GNSS authentication/attack-detection, self-calibrating mic/speaker
  array, sensor contamination) — the AI-programme-relevant point is the
  registry's method (every family carries `fcc_correlatability` and
  live-testability scores), not a P9 TPU patent: **no Edge TPU / Darwinn
  patent family appears in the canonical registry.** If a TPU patent
  claim is ever needed, it is not yet mined.

---

## 5. Contradictions & corrections vs the plan (flagged, E1-style)

1. **⚠ CONTRADICTS plan §1.5 — GXP below-HAL is not folklore.**
   Plan: "no public SDK, no documented CAPI authoring path… priced
   research thread (census + observe)". Estate: complete public ioctl ABI
   recovered from Google's kernel source, every code cross-checked in the
   shipped `.ko`, session flow recovered from `libgxp.so` disassembly,
   two ioctls **executed live** on the P9. What remains genuinely
   unbuilt is (a) CAPI *authoring* (still no public toolchain — that half
   of the plan's verdict stands) and (b) the UCI payload struct. Plan
   §1.5 and §5.1's GXP rows should be rewritten: observation is done;
   the priced item is UCI payload RE + a command-submitting probe.
2. **⚠ CORRECTS plan §1.2 — "a single add op is the smallest possible
   evidence; no real model offload proven."** The MiniLM embed_server
   partition (69/292 nodes, 7 partitions, ~97% MACs) with production
   latency/throughput numbers has existed since Oct 9–10. E2 does not
   start from zero; it starts from one measured model and one ambiguity
   (nodes vs MACs) to settle.
3. **⚠ CORRECTS plan §5.1/§5.3 framing of /dev/gxp as imaging-only.**
   The GXP driver also carries the TPU mailbox queue mapping; "GXP =
   imaging DSP, separate from the TPU" is too clean. The accurate model:
   one accelerator complex (GCIP driver), Callisto DSP cores + Darwinn
   TPU, shared mailbox infrastructure.
4. **⚠ CORRECTS E1's framing (minor) — /dev/gxp was probed before E1.**
   E1 §"Corrections" lists GXP as "PROBED at last". The node census is
   E1's (current build), but live ioctl probing happened Oct 10 on the
   pre-OTA build. No factual conflict; the plan's "never probed" gap was
   already half-closed.
5. **CONFIRMS plan §1.4 with sharper teeth — Nano.** E1's 1.7 MB AICore
   footprint + the ledger's missing `gemma3-1b-it.task` + signature-level
   permission blockers triangulate: no Nano payload is staged on this
   device and the direct paths are permission-gated. J3's kill-signal
   pricing in the plan is right.
6. **NEW — plan is silent on three live surfaces**: `wondertap0` radiotap
   monitor (BCM4390), Wi-Fi RTT responder at HAL, and NTN visibility via
   `dumpsys telephony.registry`. None are AI-plan jobs, but J1/J2's
   capture-side design should know the capture surface is richer than
   the plan describes.
7. **NEW — E2 instrumentation upgrade.** IPowerStats (µJ per component)
   and IThermal (20 types incl. TPU) are mined and live; the plan's
   battery-delta energy method and generic skin-temp sampling are the
   fallback, not the method (§2.12).
8. **CONFIRMS plan §5.1 Thread (a) and CS (a)** — ledger, E1 and the FCC
   layer all agree; no correction.

---

## 6. What this changes for the programme

- **E2 re-scopes**: it is a *second*-model bench, not a first proof. Its
  first act should re-run the known MiniLM partition on the current build
  (post-OTA) with both metrics (nodes + MAC-weighted), then add the
  classifier model. Its energy/thermal legs should use IPowerStats +
  IThermal from the start.
- **I5 (GXP census) is already done** — replace it with the UCI payload
  RE (capstone pipeline built and validated; blobs re-pullable from
  `/vendor/firmware/`) and a read-only-first command-submission probe
  design. The fence that matters is no longer "observe only" but "no
  fabricated payloads" (`gxp-below-hal-20261009.md` §8 states it exactly).
- **J1's serving pattern exists**: embed_server is a working template for
  a TPU classifier server (NNAPI delegate, HTTP/JSON, loopback lockdown,
  Magisk-persisted). J1 v1 is a model swap + retrain, not new plumbing.
- **J2's inputs upgraded**: live root-binder GNSS (54 sats/epoch,
  correlator vectors, chip PVT) + CHRE/USF sensor fusion on-device +
  IPowerStats/IThermal context. The anomaly pre-scorer can be designed
  against live streams, not just the Jul 25 corpora.
- **J3 unchanged and correctly parked**: three independent estate sources
  now agree the Nano payload/permissions gate is real.
- **Stop-looking list adopted**: UWB hardware, BT spectral FFT, Titan M2
  RE — closed by the takedown audit; the annex records them so no future
  lane re-opens them on a spec sheet.
