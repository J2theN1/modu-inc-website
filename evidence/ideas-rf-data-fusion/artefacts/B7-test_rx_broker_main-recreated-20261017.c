/*
 * test_rx_broker_main.c — host test harness for modu-bcm4390-rx-observerd
 *
 * RE-CREATED 2026-10-17 by Wren. The original harness of this name is
 * ABSENT (IDEaS pack file 31, row B7): this file is a re-creation built
 * from (a) the daemon source's own test seam and (b) the verification
 * matrix in README-rx-broker.md. It is not the original harness, and a
 * pass here is a fresh measurement of the staged daemon source, not a
 * recovery of the original run.
 *
 * Shape (from the seam): compiled with -DRX_BROKER_TEST_BACKEND, the
 * daemon's main() is compiled out and its ioctl layer routes to
 * test_backend_ioctl() below. The dispatch (handle_request) and broker
 * state are static in the daemon source, so this file #includes the
 * daemon .c to reach them.
 *
 * The stub backend holds canned radio state (channel/monitor/promisc),
 * records set-ops against it, returns a well-formed wl_sampledata_t
 * response for phy_sample_collect, and has switchable failure modes
 * (firmware rejection / short header / oversized header length).
 *
 * The checks are this harness's own decomposition of the README
 * verification matrix; the count they total is defined by this file.
 */

#include <stdio.h>
#include <string.h>
#include <stdint.h>
#include <stdlib.h>

#include "modu-bcm4390-rx-observerd.c"

/* ------------------------------------------------------------------ */
/* Stub backend                                                        */
/* ------------------------------------------------------------------ */

static uint32_t stub_channel = 36;
static uint32_t stub_monitor = 0;
static uint32_t stub_promisc = 0;
static int stub_collect_mode = 0; /* 0 normal, 1 reject, 2 short hdr, 3 bad len */
static unsigned long stub_set_calls = 0;

#define STUB_PAYLOAD_LEN 256u

int test_backend_ioctl(uint32_t cmd, int set, void *buf, uint32_t len,
                       uint32_t *used_out) {
    (void)len;
    uint32_t *u32 = (uint32_t *)buf;
    switch (cmd) {
    case WLC_GET_MAGIC:   *u32 = 0x14e46c77u; break;
    case WLC_GET_VERSION: *u32 = 2u; break;
    case WLC_GET_RADIO:   *u32 = 1u; break;
    case WLC_GET_CHANNEL: *u32 = stub_channel; break;
    case WLC_SET_CHANNEL: stub_channel = *u32; stub_set_calls++; break;
    case WLC_GET_MONITOR: *u32 = stub_monitor; break;
    case WLC_SET_MONITOR: stub_monitor = *u32 ? 1u : 0u; stub_set_calls++; break;
    case WLC_GET_PROMISC: *u32 = stub_promisc; break;
    case WLC_SET_PROMISC: stub_promisc = *u32 ? 1u : 0u; stub_set_calls++; break;
    case WLC_PHY_SAMPLE_COLLECT: {
        if (!set)
            return -(100 + 22); /* EINVAL */
        if (stub_collect_mode == 1)
            return -(100 + 5); /* firmware rejection (errno EIO) */
        wl_sampledata_t hdr;
        memset(&hdr, 0, sizeof hdr);
        hdr.tag = 0x5149;
        hdr.flag = 0;
        if (stub_collect_mode == 2) { /* short header: used < sizeof(hdr) */
            if (used_out)
                *used_out = 4;
            return 0;
        }
        if (stub_collect_mode == 3) { /* header length exceeds buffer */
            hdr.length = 0xFFFFu;
            memcpy(buf, &hdr, sizeof hdr);
            if (used_out)
                *used_out = (uint32_t)sizeof hdr + 16u;
            return 0;
        }
        hdr.length = STUB_PAYLOAD_LEN;
        memcpy(buf, &hdr, sizeof hdr);
        uint8_t *p = (uint8_t *)buf + sizeof hdr;
        for (uint32_t i = 0; i < STUB_PAYLOAD_LEN; i++)
            p[i] = (uint8_t)(i & 0xFFu);
        if (used_out)
            *used_out = (uint32_t)sizeof hdr + STUB_PAYLOAD_LEN;
        return 0;
    }
    default:
        return -(100 + 22); /* EINVAL — the daemon never sends other cmds */
    }
    if (used_out)
        *used_out = 4;
    return 0;
}

/* ------------------------------------------------------------------ */
/* Check framework                                                     */
/* ------------------------------------------------------------------ */

static int g_checks = 0;
static int g_fails = 0;
static char g_resp[RXB_SOCK_LINE_MAX];

static void check(int cond, const char *name) {
    g_checks++;
    if (cond) {
        printf("ok %d - %s\n", g_checks, name);
    } else {
        g_fails++;
        printf("FAIL %d - %s\n", g_checks, name);
    }
}

static const char *req(const char *line) {
    memset(g_resp, 0, sizeof g_resp);
    handle_request(line, g_resp, sizeof g_resp);
    return g_resp;
}

static int resp_ok(void) { return strstr(g_resp, "\"ok\":true") != NULL; }
static int resp_has(const char *sub) { return strstr(g_resp, sub) != NULL; }
static int resp_err_has(const char *sub) {
    return strstr(g_resp, "\"ok\":false") != NULL && strstr(g_resp, sub) != NULL;
}

int main(void) {
    snprintf(g_st.ifname, sizeof g_st.ifname, "wlan0");

    /* --- Dispatch by name (README matrix: op dispatch by name only) --- */

    req("{\"id\":1,\"op\":\"get_magic\"}");
    check(resp_ok(), "dispatch: get_magic answers ok");
    {
        char hex[32], dec[32];
        snprintf(hex, sizeof hex, "\"magic\":\"0x%08x\"", 0x14e46c77u);
        snprintf(dec, sizeof dec, "\"magic_u32\":%u", 0x14e46c77u);
        check(resp_has(hex) && resp_has(dec),
              "get_magic returns the proven magic value (hex + u32 pair)");
    }

    req("{\"id\":2,\"op\":\"get_version\"}");
    check(resp_ok(), "dispatch: get_version answers ok");
    check(resp_has("\"version\":2"), "get_version returns 2");

    req("{\"id\":3,\"op\":\"get_channel\"}");
    check(resp_ok(), "dispatch: get_channel answers ok");

    req("{\"id\":4,\"op\":\"get_radio\"}");
    check(resp_ok(), "dispatch: get_radio answers ok");

    req("{\"id\":5,\"op\":\"get_promisc\"}");
    check(resp_ok(), "dispatch: get_promisc answers ok");

    req("{\"id\":6,\"op\":\"get_monitor\"}");
    check(resp_ok(), "dispatch: get_monitor answers ok");

    req("{\"id\":7,\"op\":\"set_channel\",\"args\":{\"channel\":44}}");
    check(resp_ok(), "dispatch: set_channel answers ok");

    req("{\"id\":8,\"op\":\"set_promisc\",\"args\":{\"enable\":true}}");
    check(resp_ok(), "dispatch: set_promisc answers ok");

    req("{\"id\":9,\"op\":\"set_monitor\",\"args\":{\"enable\":true}}");
    check(resp_ok(), "dispatch: set_monitor answers ok");

    req("{\"id\":10,\"op\":\"phy_sample_collect\",\"args\":{\"nframes\":4}}");
    check(resp_ok(), "dispatch: phy_sample_collect answers ok");

    req("{\"id\":11,\"op\":\"restore\"}");
    check(resp_ok(), "dispatch: restore answers ok");

    req("{\"id\":12,\"op\":\"status\"}");
    check(resp_ok(), "dispatch: status answers ok");
    check(resp_has("\"schema\":\"" RXB_SCHEMA "\""),
          "status reports the broker schema string");

    /* --- Allowlist integrity --- */

    req("{\"id\":13,\"op\":\"self_destruct\"}");
    check(resp_err_has("unknown op"), "unknown op rejected");

    req("{\"id\":14,\"op\":\"raw\",\"opcode\":307}");
    check(resp_err_has("no raw opcodes"),
          "raw-opcode request rejected (no client-supplied opcodes)");

    req("{\"id\":15}");
    check(resp_err_has("missing"), "request with missing op rejected");

    /* --- Regulatory channel gate --- */

    req("{\"id\":16,\"op\":\"set_channel\",\"args\":{\"channel\":999}}");
    check(resp_err_has("not in regulatory-valid set"),
          "channel gate: 999 rejected");

    req("{\"id\":17,\"op\":\"set_channel\",\"args\":{\"channel\":14}}");
    check(resp_err_has("not in regulatory-valid set"),
          "channel gate: 14 rejected");

    req("{\"id\":18,\"op\":\"set_channel\",\"args\":{\"channel\":149}}");
    check(resp_ok(), "channel gate: 149 accepted");

    req("{\"id\":19,\"op\":\"get_channel\"}");
    check(resp_has("\"channel\":149"),
          "get_channel reflects the accepted set_channel");

    /* --- Monitor / promisc set -> get -> restore cycle --- */

    req("{\"id\":20,\"op\":\"set_monitor\",\"args\":{\"enable\":true}}");
    check(resp_ok() && resp_has("\"monitor\":true"),
          "set_monitor(true) reports monitor true");

    req("{\"id\":21,\"op\":\"get_monitor\"}");
    check(resp_has("\"monitor\":true"), "get_monitor reads back true");

    req("{\"id\":22,\"op\":\"set_promisc\",\"args\":{\"enable\":true}}");
    check(resp_ok() && resp_has("\"promisc\":true"),
          "set_promisc(true) reports promisc true");

    req("{\"id\":23,\"op\":\"get_promisc\"}");
    check(resp_has("\"promisc\":true"), "get_promisc reads back true");

    req("{\"id\":24,\"op\":\"restore\"}");
    check(resp_ok(), "restore answers ok after sets");

    req("{\"id\":25,\"op\":\"get_monitor\"}");
    check(resp_has("\"monitor\":false"),
          "restore returns monitor to its saved value (false)");

    req("{\"id\":26,\"op\":\"get_promisc\"}");
    check(resp_has("\"promisc\":false"),
          "restore returns promisc to its saved value (false)");

    /* --- Sample collect: bounds + header validation + typed errors --- */

    req("{\"id\":27,\"op\":\"phy_sample_collect\",\"args\":{\"nframes\":65}}");
    check(resp_err_has("nframes out of range"),
          "sample collect: nframes 65 rejected (range 1..64)");

    req("{\"id\":28,\"op\":\"phy_sample_collect\",\"args\":{\"nframes\":64}}");
    check(resp_ok(), "sample collect: nframes 64 accepted (upper bound)");

    req("{\"id\":29,\"op\":\"phy_sample_collect\",\"args\":{\"nframes\":4}}");
    {
        char bl[32], sc[32];
        snprintf(bl, sizeof bl, "\"byte_length\":%u",
                 (unsigned)(sizeof(wl_sampledata_t) + STUB_PAYLOAD_LEN));
        snprintf(sc, sizeof sc, "\"sample_count\":%u",
                 (unsigned)(STUB_PAYLOAD_LEN / 4));
        check(resp_ok() && resp_has(bl) && resp_has(sc),
              "sample collect: byte_length and sample_count match the stub frame");
    }
    {
        /* Recompute the expected frame and compare its SHA-256 to the
         * receipt the daemon printed. */
        uint8_t expect[sizeof(wl_sampledata_t) + STUB_PAYLOAD_LEN];
        wl_sampledata_t hdr;
        memset(&hdr, 0, sizeof hdr);
        hdr.tag = 0x5149;
        hdr.length = STUB_PAYLOAD_LEN;
        hdr.flag = 0;
        memcpy(expect, &hdr, sizeof hdr);
        for (uint32_t i = 0; i < STUB_PAYLOAD_LEN; i++)
            expect[sizeof hdr + i] = (uint8_t)(i & 0xFFu);
        char want[65];
        sha256_hex(expect, sizeof expect, want);
        const char *p = strstr(g_resp, "\"sha256\":\"");
        check(p != NULL && strncmp(p + 10, want, 64) == 0,
              "sample collect: printed sha256 matches the frame's digest");
    }

    stub_collect_mode = 2;
    req("{\"id\":30,\"op\":\"phy_sample_collect\",\"args\":{\"nframes\":4}}");
    check(resp_err_has("short header"),
          "sample collect: short firmware header becomes a typed error");
    stub_collect_mode = 3;
    req("{\"id\":31,\"op\":\"phy_sample_collect\",\"args\":{\"nframes\":4}}");
    check(resp_err_has("header length exceeds buffer"),
          "sample collect: oversized header length becomes a typed error");
    stub_collect_mode = 1;
    req("{\"id\":32,\"op\":\"phy_sample_collect\",\"args\":{\"nframes\":4}}");
    check(resp_err_has("firmware/driver rejected"),
          "sample collect: firmware rejection becomes a typed error (no crash)");
    stub_collect_mode = 0;

    /* --- Known vectors --- */

    {
        char out[65];
        sha256_hex((const uint8_t *)"abc", 3, out);
        check(strcmp(out,
                     "ba7816bf8f01cfea414140de5dae2223b00361a396177a9cb410ff"
                     "61f20015ad") == 0,
              "SHA-256 known vector: \"abc\"");
    }
    {
        char out[65];
        sha256_hex((const uint8_t *)"", 0, out);
        check(strcmp(out,
                     "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b"
                     "7852b855") == 0,
              "SHA-256 known vector: empty input");
    }
    {
        char out[16];
        b64_encode((const uint8_t *)"Man", 3, out, sizeof out);
        check(strcmp(out, "TWFu") == 0, "base64 known vector: \"Man\"");
    }
    {
        char out[16];
        b64_encode((const uint8_t *)"Ma", 2, out, sizeof out);
        check(strcmp(out, "TWE=") == 0,
              "base64 known vector: \"Ma\" (single padding)");
    }
    {
        char out[16];
        b64_encode((const uint8_t *)"M", 1, out, sizeof out);
        check(strcmp(out, "TQ==") == 0,
              "base64 known vector: \"M\" (double padding)");
    }

    printf("stub recorded %lu set-ops during the run\n", stub_set_calls);
    printf("RXB-TEST-SUMMARY: %d/%d checks passed\n",
           g_checks - g_fails, g_checks);
    return g_fails ? 1 : 0;
}
