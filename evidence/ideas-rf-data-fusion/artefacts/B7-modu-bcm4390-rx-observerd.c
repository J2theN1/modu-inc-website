/*
 * modu-bcm4390-rx-observerd — BCM4390 receive-only RX broker daemon (Pixel 9 / tokay)
 *
 * Implements the allowlisted operation set from
 *   config/zsat/pixel9_bcm4390_rx_broker.json
 *   (schema modu-pixel9-bcm4390-rx-broker/v1)
 *
 * Security properties (by construction, not by policy):
 *  - The ONLY ioctls this binary can ever issue are the 10 allowlisted
 *    opcodes below. Opcodes are compile-time constants selected by op NAME;
 *    there is no code path that accepts a client-supplied opcode number.
 *  - No transmit / packet-injection primitive exists anywhere in this binary.
 *  - set_channel validates against a regulatory channel table.
 *  - phy_sample_collect output is bounded to 10240 bytes (manifest max).
 *  - Previous channel / monitor / promisc state is saved at startup and can
 *    be restored via the "restore" op or automatically on SIGTERM/SIGINT.
 *
 * Transport: unix-domain socket, line-delimited JSON.
 *   Request:  {"id":1,"op":"get_magic"}
 *             {"id":2,"op":"set_channel","args":{"channel":44}}
 *             {"id":3,"op":"phy_sample_collect","args":{"nframes":4}}
 *   Response: {"id":1,"ok":true,"result":{...}}
 *             {"id":2,"ok":false,"error":"..."}
 *
 * Build (arm64, on Legion):
 *   aarch64-linux-gnu-gcc -O2 -static -o modu-bcm4390-rx-observerd \
 *       modu-bcm4390-rx-observerd.c
 * Build (host test, stubbed ioctl backend):
 *   gcc -O1 -g -DRX_BROKER_TEST_BACKEND -o rx_broker_test_host \
 *       modu-bcm4390-rx-observerd.c test_rx_broker_main.c
 *
 * Run (as root on P9):
 *   su -c "/data/local/tmp/modu-bcm4390-rx-observerd -i wlan0"
 */

#define _GNU_SOURCE
#include <errno.h>
#include <fcntl.h>
#include <linux/if.h>
#include <linux/sockios.h>
#include <poll.h>
#include <signal.h>
#include <stdarg.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/ioctl.h>
#include <sys/socket.h>
#include <sys/stat.h>
#include <sys/un.h>
#include <time.h>
#include <unistd.h>

/* ------------------------------------------------------------------ */
/* Manifest constants                                                  */
/* ------------------------------------------------------------------ */

#define RXB_SCHEMA "modu-pixel9-bcm4390-rx-broker/v1"
#define RXB_SAMPLE_MAX_BYTES 10240u   /* manifest: sample_buffer_max_bytes */
#define RXB_SOCK_LINE_MAX 65536
#define RXB_DEFAULT_SOCK_PATH "/data/local/tmp/modu-rx-observer.sock"

/* Allowlisted opcodes — compile-time constants. NEVER client-supplied. */
#define WLC_GET_MAGIC          0u
#define WLC_GET_VERSION        1u
#define WLC_GET_PROMISC        9u
#define WLC_SET_PROMISC        10u
#define WLC_GET_CHANNEL        29u
#define WLC_SET_CHANNEL        30u
#define WLC_GET_RADIO          37u
#define WLC_GET_MONITOR        107u
#define WLC_SET_MONITOR        108u
#define WLC_PHY_SAMPLE_COLLECT 307u

/* wl_ioctl — identical layout to the proven probe
 * (pixel9_bcm4390_readonly_ioctl_probe_v1.c) */
typedef struct wl_ioctl {
    uint32_t cmd;
    void *buf;
    uint32_t len;
    uint8_t set;
    uint8_t pad[3];
    uint32_t used;
    uint32_t needed;
} wl_ioctl_t;

/* wl_sampledata_t header preceding sample payload */
typedef struct wl_sampledata {
    uint16_t tag;
    uint16_t length;
    uint32_t flag;
} wl_sampledata_t;

/*
 * Sample-collect args for WLC_PHY_SAMPLE_COLLECT.
 *
 * LAYOUT UNVALIDATED AGAINST BCM4390 FIRMWARE (2026-10-10): the public
 * bcm4390 lineage (android-gs-akita-android16@60a0ce53) was not retrievable
 * from this lane, so this struct is a best-effort reconstruction. The broker
 * treats firmware rejection as a typed error (never a crash), and the first
 * live run of phy_sample_collect is a VALIDATION TEST, not a proven path.
 * See README-rx-broker.md.
 */
typedef struct wl_samplecollect_args {
    uint8_t coll_sz;   /* bytes per sample quantum (best effort) */
    uint8_t nframes;   /* number of frames to collect (best effort) */
    uint8_t rsvd[2];
    uint32_t flags;    /* reserved, zero */
} wl_samplecollect_args_t;

/* ------------------------------------------------------------------ */
/* Logging                                                             */
/* ------------------------------------------------------------------ */

static int g_verbose = 0;

static void log_msg(const char *fmt, ...) {
    char ts[32];
    time_t t = time(NULL);
    struct tm tmv;
    localtime_r(&t, &tmv);
    strftime(ts, sizeof ts, "%H:%M:%S", &tmv);
    fprintf(stderr, "[rx-observerd %s] ", ts);
    va_list ap;
    va_start(ap, fmt);
    vfprintf(stderr, fmt, ap);
    va_end(ap);
    fputc('\n', stderr);
}

#define LOGV(...) do { if (g_verbose) log_msg(__VA_ARGS__); } while (0)

/* ------------------------------------------------------------------ */
/* ioctl backend (real vs test stub)                                   */
/* ------------------------------------------------------------------ */

#ifdef RX_BROKER_TEST_BACKEND
/* Test stub: canned responses, records set-ops. Defined in test file. */
extern int test_backend_ioctl(uint32_t cmd, int set, void *buf, uint32_t len,
                              uint32_t *used_out);
static int g_test_mode = 1;
#else
static int g_test_mode = 0;
#endif

static int wl_do_ioctl(const char *ifname, uint32_t cmd, int set,
                       void *buf, uint32_t len, uint32_t *used_out) {
#ifdef RX_BROKER_TEST_BACKEND
    (void)ifname;
    return test_backend_ioctl(cmd, set, buf, len, used_out);
#else
    int fd = socket(AF_INET, SOCK_DGRAM, 0);
    if (fd < 0)
        return -1000 - errno;
    wl_ioctl_t ioc;
    memset(&ioc, 0, sizeof(ioc));
    ioc.cmd = cmd;
    ioc.buf = buf;
    ioc.len = len;
    ioc.set = set ? 1 : 0;
    struct ifreq ifr;
    memset(&ifr, 0, sizeof(ifr));
    snprintf(ifr.ifr_name, sizeof(ifr.ifr_name), "%s", ifname);
    ifr.ifr_data = (void *)&ioc;
    errno = 0;
    int rc = ioctl(fd, SIOCDEVPRIVATE, &ifr);
    int e = errno;
    close(fd);
    if (used_out)
        *used_out = ioc.used;
    if (rc != 0)
        return -(100 + e); /* negative: -(100+errno) */
    return 0;
#endif
}

static int wl_get_u32(const char *ifname, uint32_t cmd, uint32_t *val) {
    uint32_t v = 0;
    int rc = wl_do_ioctl(ifname, cmd, 0, &v, sizeof(v), NULL);
    if (rc == 0)
        *val = v;
    return rc;
}

static int wl_set_u32(const char *ifname, uint32_t cmd, uint32_t val) {
    return wl_do_ioctl(ifname, cmd, 1, &val, sizeof(val), NULL);
}

/* ------------------------------------------------------------------ */
/* Channel validation (regulatory-conservative)                         */
/* ------------------------------------------------------------------ */

static int channel_is_valid(uint32_t ch) {
    /* 2.4 GHz: 1..13 (14 excluded: Japan-only, keep conservative) */
    if (ch >= 1 && ch <= 13)
        return 1;
    /* 5 GHz UNII-1/2/2e/3, non-DFS + DFS listed; broker does not
     * transmit, so DFS radar-detect is not a TX concern, but we keep
     * the standard client-usable set. */
    static const uint32_t ch5[] = {
        36, 40, 44, 48, 52, 56, 60, 64,
        100, 104, 108, 112, 116, 120, 124, 128, 132, 136, 140, 144,
        149, 153, 157, 161, 165
    };
    for (size_t i = 0; i < sizeof(ch5) / sizeof(ch5[0]); i++)
        if (ch == ch5[i])
            return 1;
    return 0;
}

/* ------------------------------------------------------------------ */
/* Minimal JSON helpers (dependency-free)                               */
/* ------------------------------------------------------------------ */

/* Extract string value of "key" from a flat JSON object. Returns 1 on
 * success (out filled, NUL-terminated), 0 otherwise. */
static int json_get_str(const char *js, const char *key, char *out, size_t outsz) {
    char pat[96];
    snprintf(pat, sizeof pat, "\"%s\"", key);
    const char *p = strstr(js, pat);
    if (!p)
        return 0;
    p += strlen(pat);
    while (*p == ' ' || *p == '\t' || *p == ':')
        p++;
    if (*p == ':')
        p++;
    while (*p == ' ' || *p == '\t')
        p++;
    if (*p != '"')
        return 0;
    p++;
    size_t n = 0;
    while (*p && *p != '"' && n + 1 < outsz) {
        if (*p == '\\' && p[1]) {
            p++;
            out[n++] = *p++;
        } else {
            out[n++] = *p++;
        }
    }
    out[n] = '\0';
    return 1;
}

/* Extract unsigned integer value of "key". Returns 1 on success. */
static int json_get_u32(const char *js, const char *key, uint32_t *out) {
    char pat[96];
    snprintf(pat, sizeof pat, "\"%s\"", key);
    const char *p = strstr(js, pat);
    if (!p)
        return 0;
    p += strlen(pat);
    while (*p == ' ' || *p == '\t' || *p == ':')
        p++;
    if (*p == ':')
        p++;
    while (*p == ' ' || *p == '\t')
        p++;
    char *end = NULL;
    unsigned long v = strtoul(p, &end, 10);
    if (end == p)
        return 0;
    *out = (uint32_t)v;
    return 1;
}

/* Extract boolean value of "key" (true/false/1/0). Returns 1 on success. */
static int json_get_bool(const char *js, const char *key, int *out) {
    char pat[96];
    snprintf(pat, sizeof pat, "\"%s\"", key);
    const char *p = strstr(js, pat);
    if (!p)
        return 0;
    p += strlen(pat);
    while (*p == ' ' || *p == '\t' || *p == ':')
        p++;
    if (*p == ':')
        p++;
    while (*p == ' ' || *p == '\t')
        p++;
    if (strncmp(p, "true", 4) == 0) {
        *out = 1;
        return 1;
    }
    if (strncmp(p, "false", 5) == 0) {
        *out = 0;
        return 1;
    }
    if (*p == '1') {
        *out = 1;
        return 1;
    }
    if (*p == '0') {
        *out = 0;
        return 1;
    }
    return 0;
}

/* JSON-escape a string into out (outsz includes NUL). */
static void json_escape(const char *in, char *out, size_t outsz) {
    size_t n = 0;
    for (; *in && n + 2 < outsz; in++) {
        unsigned char c = (unsigned char)*in;
        if (c == '"' || c == '\\') {
            out[n++] = '\\';
            out[n++] = (char)c;
        } else if (c < 0x20) {
            if (n + 7 >= outsz)
                break;
            n += snprintf(out + n, outsz - n, "\\u%04x", c);
        } else {
            out[n++] = (char)c;
        }
    }
    out[n] = '\0';
}

/* ------------------------------------------------------------------ */
/* Base64 (for sample payloads)                                         */
/* ------------------------------------------------------------------ */

static const char b64tab[] =
    "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/";

static size_t b64_encode(const uint8_t *in, size_t len, char *out, size_t outsz) {
    size_t need = ((len + 2) / 3) * 4 + 1;
    if (need > outsz)
        return 0;
    size_t o = 0;
    for (size_t i = 0; i < len; i += 3) {
        uint32_t v = (uint32_t)in[i] << 16;
        if (i + 1 < len)
            v |= (uint32_t)in[i + 1] << 8;
        if (i + 2 < len)
            v |= in[i + 2];
        out[o++] = b64tab[(v >> 18) & 63];
        out[o++] = b64tab[(v >> 12) & 63];
        out[o++] = (i + 1 < len) ? b64tab[(v >> 6) & 63] : '=';
        out[o++] = (i + 2 < len) ? b64tab[v & 63] : '=';
    }
    out[o] = '\0';
    return o;
}

/* ------------------------------------------------------------------ */
/* SHA-256 (compact, public-domain style implementation)                */
/* ------------------------------------------------------------------ */

typedef struct {
    uint32_t h[8];
    uint8_t buf[64];
    size_t buflen;
    uint64_t total;
} sha256_ctx;

static uint32_t rotr32(uint32_t x, int n) { return (x >> n) | (x << (32 - n)); }

static void sha256_block(sha256_ctx *c, const uint8_t *p) {
    static const uint32_t K[64] = {
        0x428a2f98, 0x71374491, 0xb5c0fbcf, 0xe9b5dba5, 0x3956c25b, 0x59f111f1,
        0x923f82a4, 0xab1c5ed5, 0xd807aa98, 0x12835b01, 0x243185be, 0x550c7dc3,
        0x72be5d74, 0x80deb1fe, 0x9bdc06a7, 0xc19bf174, 0xe49b69c1, 0xefbe4786,
        0x0fc19dc6, 0x240ca1cc, 0x2de92c6f, 0x4a7484aa, 0x5cb0a9dc, 0x76f988da,
        0x983e5152, 0xa831c66d, 0xb00327c8, 0xbf597fc7, 0xc6e00bf3, 0xd5a79147,
        0x06ca6351, 0x14292967, 0x27b70a85, 0x2e1b2138, 0x4d2c6dfc, 0x53380d13,
        0x650a7354, 0x766a0abb, 0x81c2c92e, 0x92722c85, 0xa2bfe8a1, 0xa81a664b,
        0xc24b8b70, 0xc76c51a3, 0xd192e819, 0xd6990624, 0xf40e3585, 0x106aa070,
        0x19a4c116, 0x1e376c08, 0x2748774c, 0x34b0bcb5, 0x391c0cb3, 0x4ed8aa4a,
        0x5b9cca4f, 0x682e6ff3, 0x748f82ee, 0x78a5636f, 0x84c87814, 0x8cc70208,
        0x90befffa, 0xa4506ceb, 0xbef9a3f7, 0xc67178f2
    };
    uint32_t w[64];
    for (int i = 0; i < 16; i++)
        w[i] = ((uint32_t)p[i * 4] << 24) | ((uint32_t)p[i * 4 + 1] << 16) |
               ((uint32_t)p[i * 4 + 2] << 8) | p[i * 4 + 3];
    for (int i = 16; i < 64; i++) {
        uint32_t s0 = rotr32(w[i - 15], 7) ^ rotr32(w[i - 15], 18) ^ (w[i - 15] >> 3);
        uint32_t s1 = rotr32(w[i - 2], 17) ^ rotr32(w[i - 2], 19) ^ (w[i - 2] >> 10);
        w[i] = w[i - 16] + s0 + w[i - 7] + s1;
    }
    uint32_t a = c->h[0], b = c->h[1], cc = c->h[2], d = c->h[3];
    uint32_t e = c->h[4], f = c->h[5], g = c->h[6], h = c->h[7];
    for (int i = 0; i < 64; i++) {
        uint32_t S1 = rotr32(e, 6) ^ rotr32(e, 11) ^ rotr32(e, 25);
        uint32_t ch = (e & f) ^ (~e & g);
        uint32_t t1 = h + S1 + ch + K[i] + w[i];
        uint32_t S0 = rotr32(a, 2) ^ rotr32(a, 13) ^ rotr32(a, 22);
        uint32_t maj = (a & b) ^ (a & cc) ^ (b & cc);
        uint32_t t2 = S0 + maj;
        h = g;
        g = f;
        f = e;
        e = d + t1;
        d = cc;
        cc = b;
        b = a;
        a = t1 + t2;
    }
    c->h[0] += a;
    c->h[1] += b;
    c->h[2] += cc;
    c->h[3] += d;
    c->h[4] += e;
    c->h[5] += f;
    c->h[6] += g;
    c->h[7] += h;
}

static void sha256_init(sha256_ctx *c) {
    c->h[0] = 0x6a09e667;
    c->h[1] = 0xbb67ae85;
    c->h[2] = 0x3c6ef372;
    c->h[3] = 0xa54ff53a;
    c->h[4] = 0x510e527f;
    c->h[5] = 0x9b05688c;
    c->h[6] = 0x1f83d9ab;
    c->h[7] = 0x5be0cd19;
    c->buflen = 0;
    c->total = 0;
}

static void sha256_update(sha256_ctx *c, const uint8_t *data, size_t len) {
    c->total += len;
    while (len) {
        size_t take = 64 - c->buflen;
        if (take > len)
            take = len;
        memcpy(c->buf + c->buflen, data, take);
        c->buflen += take;
        data += take;
        len -= take;
        if (c->buflen == 64) {
            sha256_block(c, c->buf);
            c->buflen = 0;
        }
    }
}

static void sha256_final(sha256_ctx *c, uint8_t out[32]) {
    uint64_t bits = c->total * 8;
    uint8_t pad = 0x80;
    sha256_update(c, &pad, 1);
    uint8_t zero = 0;
    while (c->buflen != 56)
        sha256_update(c, &zero, 1);
    uint8_t lenb[8];
    for (int i = 0; i < 8; i++)
        lenb[i] = (uint8_t)(bits >> (56 - 8 * i));
    /* finalize without re-padding */
    memcpy(c->buf + 56, lenb, 8);
    sha256_block(c, c->buf);
    for (int i = 0; i < 8; i++) {
        out[i * 4] = (uint8_t)(c->h[i] >> 24);
        out[i * 4 + 1] = (uint8_t)(c->h[i] >> 16);
        out[i * 4 + 2] = (uint8_t)(c->h[i] >> 8);
        out[i * 4 + 3] = (uint8_t)c->h[i];
    }
}

static void sha256_hex(const uint8_t *data, size_t len, char out[65]) {
    sha256_ctx c;
    uint8_t dig[32];
    sha256_init(&c);
    sha256_update(&c, data, len);
    sha256_final(&c, dig);
    for (int i = 0; i < 32; i++)
        snprintf(out + i * 2, 3, "%02x", dig[i]);
    out[64] = '\0';
}

/* ------------------------------------------------------------------ */
/* Broker state                                                         */
/* ------------------------------------------------------------------ */

struct broker_state {
    char ifname[IFNAMSIZ];
    char sock_path[108];
    /* saved state for restore */
    int have_saved_channel;
    uint32_t saved_channel;
    int have_saved_monitor;
    uint32_t saved_monitor;
    int have_saved_promisc;
    uint32_t saved_promisc;
    unsigned long req_count;
    unsigned long err_count;
};

static struct broker_state g_st;
static volatile sig_atomic_t g_stop = 0;

static void on_signal(int sig) {
    (void)sig;
    g_stop = 1;
}

/* Save current channel/monitor/promisc so set_* ops are reversible. */
static void save_current_state(const char *ifname) {
    uint32_t v;
    if (wl_get_u32(ifname, WLC_GET_CHANNEL, &v) == 0) {
        g_st.saved_channel = v;
        g_st.have_saved_channel = 1;
    }
    if (wl_get_u32(ifname, WLC_GET_MONITOR, &v) == 0) {
        g_st.saved_monitor = v;
        g_st.have_saved_monitor = 1;
    }
    if (wl_get_u32(ifname, WLC_GET_PROMISC, &v) == 0) {
        g_st.saved_promisc = v;
        g_st.have_saved_promisc = 1;
    }
    LOGV("saved state: channel=%s%u monitor=%s%u promisc=%s%u",
         g_st.have_saved_channel ? "" : "(unknown) ", g_st.saved_channel,
         g_st.have_saved_monitor ? "" : "(unknown) ", g_st.saved_monitor,
         g_st.have_saved_promisc ? "" : "(unknown) ", g_st.saved_promisc);
}

static void restore_saved_state(const char *ifname) {
    if (g_st.have_saved_monitor) {
        int rc = wl_set_u32(ifname, WLC_SET_MONITOR, g_st.saved_monitor);
        log_msg("restore monitor -> %u rc=%d", g_st.saved_monitor, rc);
    }
    if (g_st.have_saved_promisc) {
        int rc = wl_set_u32(ifname, WLC_SET_PROMISC, g_st.saved_promisc);
        log_msg("restore promisc -> %u rc=%d", g_st.saved_promisc, rc);
    }
    if (g_st.have_saved_channel) {
        int rc = wl_set_u32(ifname, WLC_SET_CHANNEL, g_st.saved_channel);
        log_msg("restore channel -> %u rc=%d", g_st.saved_channel, rc);
    }
}

/* ------------------------------------------------------------------ */
/* Op implementations                                                   */
/* ------------------------------------------------------------------ */

/* Response buffer helpers: build JSON into resp (RXB_SOCK_LINE_MAX). */
static void resp_ok_u32(char *resp, size_t rsz, uint32_t id,
                        const char *field, uint32_t val) {
    snprintf(resp, rsz, "{\"id\":%u,\"ok\":true,\"result\":{\"%s\":%u}}",
             id, field, val);
}

static void resp_ok_bool(char *resp, size_t rsz, uint32_t id,
                         const char *field, int val) {
    snprintf(resp, rsz, "{\"id\":%u,\"ok\":true,\"result\":{\"%s\":%s}}",
             id, field, val ? "true" : "false");
}

static void resp_err(char *resp, size_t rsz, uint32_t id, const char *msg) {
    char esc[512];
    json_escape(msg, esc, sizeof esc);
    snprintf(resp, rsz, "{\"id\":%u,\"ok\":false,\"error\":\"%s\"}", id, esc);
    g_st.err_count++;
}

static void resp_ioctl_err(char *resp, size_t rsz, uint32_t id,
                           const char *what, int rc) {
    char msg[256];
    if (rc <= -1100)
        snprintf(msg, sizeof msg, "%s: socket/ioctl setup failed (%d)", what, rc);
    else if (rc < 0)
        snprintf(msg, sizeof msg, "%s: firmware/driver rejected (errno=%d)", what, -(rc + 100));
    else
        snprintf(msg, sizeof msg, "%s: failed rc=%d", what, rc);
    resp_err(resp, rsz, id, msg);
}

/* phy_sample_collect: bounded, validated, hashed.
 * Returns 0 on success with resp filled, -1 on error with resp filled. */
static int op_phy_sample_collect(const char *ifname, uint32_t id,
                                 const char *req, char *resp, size_t rsz) {
    uint32_t nframes = 4;
    json_get_u32(req, "nframes", &nframes);
    if (nframes < 1)
        nframes = 1;
    if (nframes > 64) {
        resp_err(resp, rsz, id, "nframes out of range (1..64)");
        return -1;
    }

    wl_samplecollect_args_t args;
    memset(&args, 0, sizeof(args));
    args.coll_sz = 8; /* best effort; see UNVALIDATED note above */
    args.nframes = (uint8_t)nframes;

    static uint8_t sbuf[RXB_SAMPLE_MAX_BYTES];
    memset(sbuf, 0, sizeof(sbuf));
    /* Overlay args at the head; firmware writes sample data after.
     * Bounded: never more than RXB_SAMPLE_MAX_BYTES total. */
    memcpy(sbuf, &args, sizeof(args));
    uint32_t used = 0;
    int rc = wl_do_ioctl(ifname, WLC_PHY_SAMPLE_COLLECT, 1,
                         sbuf, sizeof(sbuf), &used);
    if (rc != 0) {
        resp_ioctl_err(resp, rsz, id, "phy_sample_collect", rc);
        return -1;
    }

    /* Validate wl_sampledata_t header. */
    if (used < sizeof(wl_sampledata_t)) {
        resp_err(resp, rsz, id, "phy_sample_collect: short header from firmware");
        return -1;
    }
    wl_sampledata_t hdr;
    memcpy(&hdr, sbuf, sizeof(hdr));
    if (hdr.length > sizeof(sbuf) - sizeof(hdr)) {
        resp_err(resp, rsz, id, "phy_sample_collect: header length exceeds buffer");
        return -1;
    }
    uint32_t payload_len = hdr.length;
    uint32_t total = (uint32_t)sizeof(hdr) + payload_len;
    if (total > used)
        total = used; /* trust actual bytes over header */

    /* IQ sample count: int16 (I,Q) pairs per manifest contract. */
    uint32_t nsamples = payload_len / 4;

    char sha[65];
    sha256_hex(sbuf, total, sha);

    /* Current channel for metadata. */
    uint32_t ch = 0;
    wl_get_u32(ifname, WLC_GET_CHANNEL, &ch);

    /* Base64 payload: bound output size. */
    size_t b64need = ((total + 2) / 3) * 4 + 1;
    char *b64 = malloc(b64need);
    if (!b64) {
        resp_err(resp, rsz, id, "phy_sample_collect: out of memory");
        return -1;
    }
    b64_encode(sbuf, total, b64, b64need);

    /* Keep the JSON line bounded: truncate b64 in the response if needed
     * (full data is still hashed; receipt is the point). */
    int n = snprintf(resp, rsz,
                     "{\"id\":%u,\"ok\":true,\"result\":{"
                     "\"tag\":%u,\"flag\":%u,"
                     "\"sample_count\":%u,\"byte_length\":%u,"
                     "\"channel\":%u,\"sha256\":\"%s\",\"data_b64\":\"",
                     id, hdr.tag, hdr.flag, nsamples, total, ch, sha);
    size_t room = (n > 0 && (size_t)n < rsz - 64) ? (rsz - (size_t)n - 64) : 0;
    if (strlen(b64) > room && room > 0) {
        /* Emit truncated marker rather than overflowing the line. */
        strncat(resp, b64, room - 32);
        strcat(resp, "...\",\"truncated\":true}}");
    } else if (room > 0) {
        strcat(resp, b64);
        strcat(resp, "\"}}");
    } else {
        free(b64);
        resp_err(resp, rsz, id, "phy_sample_collect: response too large");
        return -1;
    }
    free(b64);
    return 0;
}

/* ------------------------------------------------------------------ */
/* Request dispatch — the allowlist. No client-supplied opcodes exist.  */
/* ------------------------------------------------------------------ */

static void handle_request(const char *line, char *resp, size_t rsz) {
    uint32_t id = 0;
    json_get_u32(line, "id", &id);
    char op[64];
    if (!json_get_str(line, "op", op, sizeof op)) {
        resp_err(resp, rsz, id, "missing \"op\"");
        return;
    }
    const char *ifname = g_st.ifname;
    g_st.req_count++;
    LOGV("req id=%u op=%s", id, op);

    uint32_t v;
    int rc;

    if (strcmp(op, "get_magic") == 0) {
        rc = wl_get_u32(ifname, WLC_GET_MAGIC, &v);
        if (rc == 0) {
            char hex[16];
            snprintf(hex, sizeof hex, "0x%08x", v);
            char ehex[32];
            json_escape(hex, ehex, sizeof ehex);
            snprintf(resp, rsz,
                     "{\"id\":%u,\"ok\":true,\"result\":{\"magic\":\"%s\",\"magic_u32\":%u}}",
                     id, ehex, v);
        } else {
            resp_ioctl_err(resp, rsz, id, "get_magic", rc);
        }
    } else if (strcmp(op, "get_version") == 0) {
        rc = wl_get_u32(ifname, WLC_GET_VERSION, &v);
        if (rc == 0)
            resp_ok_u32(resp, rsz, id, "version", v);
        else
            resp_ioctl_err(resp, rsz, id, "get_version", rc);
    } else if (strcmp(op, "get_channel") == 0) {
        rc = wl_get_u32(ifname, WLC_GET_CHANNEL, &v);
        if (rc == 0)
            resp_ok_u32(resp, rsz, id, "channel", v);
        else
            resp_ioctl_err(resp, rsz, id, "get_channel", rc);
    } else if (strcmp(op, "set_channel") == 0) {
        uint32_t ch;
        if (!json_get_u32(line, "channel", &ch)) {
            resp_err(resp, rsz, id, "set_channel needs args.channel");
            return;
        }
        if (!channel_is_valid(ch)) {
            char m[128];
            snprintf(m, sizeof m, "channel %u not in regulatory-valid set", ch);
            resp_err(resp, rsz, id, m);
            return;
        }
        uint32_t prev = 0;
        wl_get_u32(ifname, WLC_GET_CHANNEL, &prev);
        rc = wl_set_u32(ifname, WLC_SET_CHANNEL, ch);
        if (rc == 0) {
            g_st.saved_channel = prev;
            g_st.have_saved_channel = 1;
            snprintf(resp, rsz,
                     "{\"id\":%u,\"ok\":true,\"result\":{\"channel\":%u,\"previous_channel\":%u}}",
                     id, ch, prev);
        } else {
            resp_ioctl_err(resp, rsz, id, "set_channel", rc);
        }
    } else if (strcmp(op, "get_radio") == 0) {
        rc = wl_get_u32(ifname, WLC_GET_RADIO, &v);
        if (rc == 0)
            resp_ok_u32(resp, rsz, id, "radio", v);
        else
            resp_ioctl_err(resp, rsz, id, "get_radio", rc);
    } else if (strcmp(op, "get_promisc") == 0) {
        rc = wl_get_u32(ifname, WLC_GET_PROMISC, &v);
        if (rc == 0)
            resp_ok_bool(resp, rsz, id, "promisc", v != 0);
        else
            resp_ioctl_err(resp, rsz, id, "get_promisc", rc);
    } else if (strcmp(op, "set_promisc") == 0) {
        int en;
        if (!json_get_bool(line, "enable", &en)) {
            resp_err(resp, rsz, id, "set_promisc needs args.enable (bool)");
            return;
        }
        uint32_t prev = 0;
        wl_get_u32(ifname, WLC_GET_PROMISC, &prev);
        rc = wl_set_u32(ifname, WLC_SET_PROMISC, en ? 1u : 0u);
        if (rc == 0) {
            g_st.saved_promisc = prev;
            g_st.have_saved_promisc = 1;
            resp_ok_bool(resp, rsz, id, "promisc", en);
        } else {
            resp_ioctl_err(resp, rsz, id, "set_promisc", rc);
        }
    } else if (strcmp(op, "get_monitor") == 0) {
        rc = wl_get_u32(ifname, WLC_GET_MONITOR, &v);
        if (rc == 0)
            resp_ok_bool(resp, rsz, id, "monitor", v != 0);
        else
            resp_ioctl_err(resp, rsz, id, "get_monitor", rc);
    } else if (strcmp(op, "set_monitor") == 0) {
        int en;
        if (!json_get_bool(line, "enable", &en)) {
            resp_err(resp, rsz, id, "set_monitor needs args.enable (bool)");
            return;
        }
        uint32_t prev = 0;
        wl_get_u32(ifname, WLC_GET_MONITOR, &prev);
        rc = wl_set_u32(ifname, WLC_SET_MONITOR, en ? 1u : 0u);
        if (rc == 0) {
            g_st.saved_monitor = prev;
            g_st.have_saved_monitor = 1;
            resp_ok_bool(resp, rsz, id, "monitor", en);
        } else {
            resp_ioctl_err(resp, rsz, id, "set_monitor", rc);
        }
    } else if (strcmp(op, "phy_sample_collect") == 0) {
        op_phy_sample_collect(ifname, id, line, resp, rsz);
    } else if (strcmp(op, "restore") == 0) {
        restore_saved_state(ifname);
        snprintf(resp, rsz, "{\"id\":%u,\"ok\":true,\"result\":{\"restored\":true}}", id);
    } else if (strcmp(op, "status") == 0) {
        char chb[32], mob[32], prb[32];
        if (g_st.have_saved_channel)
            snprintf(chb, sizeof chb, "%u", g_st.saved_channel);
        else
            snprintf(chb, sizeof chb, "null");
        if (g_st.have_saved_monitor)
            snprintf(mob, sizeof mob, "%u", g_st.saved_monitor);
        else
            snprintf(mob, sizeof mob, "null");
        if (g_st.have_saved_promisc)
            snprintf(prb, sizeof prb, "%u", g_st.saved_promisc);
        else
            snprintf(prb, sizeof prb, "null");
        snprintf(resp, rsz,
                 "{\"id\":%u,\"ok\":true,\"result\":{"
                 "\"schema\":\"%s\",\"ifname\":\"%s\","
                 "\"requests\":%lu,\"errors\":%lu,"
                 "\"saved\":{\"channel\":%s,\"monitor\":%s,\"promisc\":%s}}}",
                 id, RXB_SCHEMA, ifname,
                 g_st.req_count, g_st.err_count, chb, mob, prb);
    } else {
        char m[160];
        snprintf(m, sizeof m,
                 "unknown op \"%s\" — allowlisted ops only, no raw opcodes", op);
        resp_err(resp, rsz, id, m);
    }
}

#ifndef RX_BROKER_TEST_BACKEND
/* ------------------------------------------------------------------ */
/* Daemon main                                                         */
/* ------------------------------------------------------------------ */

static int g_listen_fd = -1;

static void cleanup_socket(void) {
    if (g_listen_fd >= 0)
        close(g_listen_fd);
    unlink(g_st.sock_path);
}

static ssize_t read_line(int fd, char *buf, size_t cap) {
    size_t n = 0;
    while (n + 1 < cap) {
        char c;
        ssize_t r = read(fd, &c, 1);
        if (r <= 0)
            return (n > 0) ? (ssize_t)n : r;
        if (c == '\n')
            break;
        if (c != '\r')
            buf[n++] = c;
    }
    buf[n] = '\0';
    return (ssize_t)n;
}

static void serve_client(int cfd) {
    char line[RXB_SOCK_LINE_MAX];
    char resp[RXB_SOCK_LINE_MAX];
    for (;;) {
        ssize_t n = read_line(cfd, line, sizeof(line));
        if (n <= 0)
            break;
        if (n == 0 || line[0] == '\0')
            continue;
        memset(resp, 0, sizeof(resp));
        handle_request(line, resp, sizeof(resp));
        size_t rl = strlen(resp);
        resp[rl] = '\n';
        /* write all */
        size_t off = 0;
        while (off <= rl) {
            ssize_t w = write(cfd, resp + off, rl + 1 - off);
            if (w <= 0)
                break;
            off += (size_t)w;
        }
        if (g_stop)
            break;
    }
}

static void usage(const char *prog) {
    fprintf(stderr,
            "usage: %s [-i ifname] [-s sockpath] [-v]\n"
            "  BCM4390 receive-only RX broker daemon (schema %s)\n",
            prog, RXB_SCHEMA);
}

int main(int argc, char **argv) {
    snprintf(g_st.ifname, sizeof(g_st.ifname), "wlan0");
    snprintf(g_st.sock_path, sizeof(g_st.sock_path), "%s", RXB_DEFAULT_SOCK_PATH);

    int opt;
    while ((opt = getopt(argc, argv, "i:s:vh")) != -1) {
        switch (opt) {
        case 'i':
            snprintf(g_st.ifname, sizeof(g_st.ifname), "%s", optarg);
            break;
        case 's':
            snprintf(g_st.sock_path, sizeof(g_st.sock_path), "%s", optarg);
            break;
        case 'v':
            g_verbose = 1;
            break;
        default:
            usage(argv[0]);
            return 2;
        }
    }

    signal(SIGTERM, on_signal);
    signal(SIGINT, on_signal);
    signal(SIGPIPE, SIG_IGN);

    if (getuid() != 0 && !g_test_mode)
        log_msg("WARNING: not running as uid 0 — private ioctls will fail (errno 13)");

    /* Save pre-existing radio state before serving. */
    save_current_state(g_st.ifname);

    unlink(g_st.sock_path);
    g_listen_fd = socket(AF_UNIX, SOCK_STREAM, 0);
    if (g_listen_fd < 0) {
        perror("socket");
        return 1;
    }
    struct sockaddr_un addr;
    memset(&addr, 0, sizeof(addr));
    addr.sun_family = AF_UNIX;
    snprintf(addr.sun_path, sizeof(addr.sun_path), "%s", g_st.sock_path);
    if (bind(g_listen_fd, (struct sockaddr *)&addr, sizeof(addr)) != 0) {
        perror("bind");
        return 1;
    }
    chmod(g_st.sock_path, 0666); /* clients run as other uids */
    if (listen(g_listen_fd, 8) != 0) {
        perror("listen");
        cleanup_socket();
        return 1;
    }
    atexit(cleanup_socket);

    log_msg("listening on %s (ifname=%s, schema=%s)",
            g_st.sock_path, g_st.ifname, RXB_SCHEMA);

    struct pollfd pfd = { .fd = g_listen_fd, .events = POLLIN };
    while (!g_stop) {
        int pr = poll(&pfd, 1, 500);
        if (pr < 0) {
            if (errno == EINTR)
                continue;
            perror("poll");
            break;
        }
        if (pr == 0)
            continue;
        int cfd = accept(g_listen_fd, NULL, NULL);
        if (cfd < 0) {
            if (errno == EINTR)
                continue;
            perror("accept");
            continue;
        }
        LOGV("client connected");
        serve_client(cfd);
        close(cfd);
        LOGV("client disconnected");
    }

    log_msg("shutting down — restoring radio state");
    restore_saved_state(g_st.ifname);
    return 0;
}
#endif /* !RX_BROKER_TEST_BACKEND */
