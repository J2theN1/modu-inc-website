# modu-bcm4390-rx-observerd — BCM4390 RX Broker

**Status:** Implemented 2026-10-10. Host-tested (37/37 checks pass). ARM64 binary
built. **Live P9 validation pending** (P9 offline at build time).

**Work queue:** P9-RXBOKER — "biggest unlock, no AOSP needed."

## What it is

A privileged, **receive-only** broker daemon for the Pixel 9's BCM4390 WiFi chip.
It exposes the allowlisted diagnostic-receive operations from the estate design
(`config/zsat/pixel9_bcm4390_rx_broker.json`, schema
`modu-pixel9-bcm4390-rx-broker/v1`) without granting a general CAP_NET_ADMIN
shell or arbitrary private-ioctl access.

This is the closest thing to an SDR tap on stock hardware: monitor mode +
PHY IQ sample collection, through a typed request contract.

## What it unlocks

| Op | What it gives |
|---|---|
| `get_magic` / `get_version` | Driver handshake (proven: `0x14e46c77` / `2`) |
| `get_channel` / `set_channel` | Read + regulatory-validated channel changes |
| `get_monitor` / `set_monitor` | Monitor mode toggle (receive-only capture path) |
| `get_promisc` / `set_promisc` | Promiscuous mode toggle |
| `get_radio` | Radio state |
| `phy_sample_collect` | **Raw IQ samples** (int16 I/Q per core, ≤10240 B, sha256 receipt) |
| `restore` | Restore pre-broker channel/monitor/promisc state |
| `status` | Broker introspection |

## Security properties (by construction)

1. **No raw opcodes.** The 10 opcodes are compile-time constants dispatched by
   op *name*. There is no code path that accepts a client-supplied opcode
   number — `{"op":"raw","opcode":307}` is rejected.
2. **No TX.** No transmit or packet-injection primitive exists in the binary.
3. **Regulatory channel gate.** `set_channel` accepts only 1–13 (2.4 GHz) and
   the standard 5 GHz client set; everything else is rejected before any ioctl.
4. **Bounded samples.** `phy_sample_collect` caps at 10240 bytes (manifest max),
   `nframes` 1–64, and validates the `wl_sampledata_t` header before returning
   data. Firmware rejection becomes a typed error, never a crash.
5. **State restore.** Previous channel/monitor/promisc are saved at startup,
   updated on every set_*, restorable via `restore`, and auto-restored on
   SIGTERM/SIGINT.

## Files

| File | Purpose |
|---|---|
| `modu-bcm4390-rx-observerd.c` | The daemon (C, dependency-free: no libc JSON, no OpenSSL) |
| `rx_observer_client.py` | Typed Python client (socket + JSON) |
| `test_rx_broker_main.c` | Host test harness (stubbed ioctl backend) |
| `Makefile` | `make test` (host), `make arm64` (Legion) |

## Protocol

Unix-domain socket, line-delimited JSON. Default path
`/data/local/tmp/modu-rx-observer.sock`.

```
→ {"id":1,"op":"get_magic"}
← {"id":1,"ok":true,"result":{"magic":"0x14e46c77","magic_u32":351283263}}

→ {"id":2,"op":"set_channel","args":{"channel":44}}
← {"id":2,"ok":true,"result":{"channel":44,"previous_channel":36}}

→ {"id":3,"op":"set_channel","args":{"channel":999}}
← {"id":3,"ok":false,"error":"channel 999 not in regulatory-valid set"}

→ {"id":4,"op":"phy_sample_collect","args":{"nframes":4}}
← {"id":4,"ok":true,"result":{"tag":...,"sample_count":...,"byte_length":...,
    "channel":44,"sha256":"...","data_b64":"..."}}
```

## Build

Host tests (no P9 needed):
```
make test        # 37 checks, stubbed ioctl backend
```

ARM64 daemon (on Legion):
```
make arm64       # aarch64-linux-gnu-gcc -O2 -static
```

## Deploy (pending P9)

```sh
# on Legion:
adb push modu-bcm4390-rx-observerd /data/local/tmp/
adb push rx_observer_client.py /data/local/tmp/
adb shell "chmod 755 /data/local/tmp/modu-bcm4390-rx-observerd"
# start (as root; private ioctls need uid 0):
adb shell "su -c '/data/local/tmp/modu-bcm4390-rx-observerd -i wlan0 -v &'"
# use:
adb shell "python3 /data/local/tmp/rx_observer_client.py get_magic"
```

## Verification matrix

| Check | Where | Status |
|---|---|---|
| Manifest schema/allowlist intact | host | ✅ existing estate test |
| Op dispatch by name only | host | ✅ 37/37 |
| Unknown op rejected | host | ✅ |
| Raw opcode injection impossible | host | ✅ |
| Channel 999/14 rejected, 44/149 accepted | host | ✅ |
| Monitor/promisc set→get→restore cycle | host | ✅ (stub) |
| Sample collect bounds + header validation | host | ✅ (stub) |
| Firmware rejection → typed error | host | ✅ (stub) |
| SHA-256 known vector | host | ✅ |
| Base64 known vector | host | ✅ |
| ARM64 static binary builds | Legion | ✅ ELF aarch64, 853 KB |
| `get_magic` returns `0x14e46c77` on P9 | P9 | ⏳ pending (P9 offline) |
| `get_channel` live read | P9 | ⏳ pending |
| Monitor toggle + restore without assoc corruption | P9 | ⏳ pending |
| `phy_sample_collect` firmware acceptance | P9 | ⏳ **validation test** — args layout unvalidated (see below) |

## Known limitation: sample-collect args layout

The `wl_samplecollect_args_t` layout sent with `WLC_PHY_SAMPLE_COLLECT` (307)
is a **best-effort reconstruction** — the public bcm4390 lineage
(`android-gs-akita-android16@60a0ce53`) was not retrievable from this lane, and
no authoritative struct definition was found. The broker:

- sends a conservative, zeroed args block with only `coll_sz`/`nframes` set,
- bounds the response buffer to 10240 bytes,
- validates the `wl_sampledata_t` header (`tag`/`length` sanity) before
  trusting any payload,
- converts firmware rejection into a typed JSON error.

**The first live `phy_sample_collect` run is a validation test.** If the
firmware rejects the args shape, the error is clean and the remaining 9 ops
are unaffected. Correct the struct against the live result at that point.

## Design lineage

- Design: `modu-rf-lab/.worktrees/rf-fabric-convergence-20260822/config/zsat/pixel9_bcm4390_rx_broker.json`
- Probe foundation: `scripts/pixel9_bcm4390_readonly_ioctl_probe_v1.c`
  (proven `WLC_GET_MAGIC`/`WLC_GET_VERSION` as uid 0 on P9, 2026-10-08)
- ioctl mechanics: `SIOCDEVPRIVATE` + `struct wl_ioctl` (same as probe)
- Research: `goals/pixel-9-lab-build-out/hidden_files/retrofit-local-research-20261008.md`

## Suggested git home

`modu-rf-lab/tools/rx-broker/` (or `privileged/`), alongside the existing
`config/zsat/` manifest. Landing is the parent agent's call.
