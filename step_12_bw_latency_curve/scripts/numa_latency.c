// Copyright (c) 2026
// SPDX-License-Identifier: BSD-3-Clause

#define _GNU_SOURCE

#include <inttypes.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

static void
enter_roi(void)
{
    fflush(stdout);
    fprintf(stderr, "LAT_INFO setup complete, requesting ROI switch\n");
    fflush(stderr);
    const int rc = system("gem5-bridge hypercall 4");
    if (rc != 0) {
        fprintf(stderr, "gem5-bridge hypercall 4 failed with rc=%d\n", rc);
        exit(1);
    }
}

enum {
    CACHELINE_BYTES = 64,
};

static void
usage(const char *prog)
{
    fprintf(stderr,
            "usage: %s <node> <latency_MiB> <latency_iterations> [cpu_mhz]\n",
            prog);
    exit(2);
}

static long
parse_long_arg(const char *text, const char *name)
{
    char *end = NULL;
    const long value = strtol(text, &end, 10);
    if (text[0] == '\0' || end == NULL || *end != '\0') {
        fprintf(stderr, "invalid %s: %s\n", name, text);
        exit(2);
    }
    return value;
}

static uint64_t
parse_u64_arg(const char *text, const char *name)
{
    char *end = NULL;
    const unsigned long long value = strtoull(text, &end, 10);
    if (text[0] == '\0' || end == NULL || *end != '\0') {
        fprintf(stderr, "invalid %s: %s\n", name, text);
        exit(2);
    }
    return (uint64_t)value;
}

static double
parse_double_arg(const char *text, const char *name)
{
    char *end = NULL;
    const double value = strtod(text, &end);
    if (text[0] == '\0' || end == NULL || *end != '\0') {
        fprintf(stderr, "invalid %s: %s\n", name, text);
        exit(2);
    }
    return value;
}

static inline uint64_t
rdtsc_begin(void)
{
    unsigned lo;
    unsigned hi;
    __asm__ __volatile__("lfence\n\t"
                         "rdtsc\n\t"
                         : "=a"(lo), "=d"(hi)
                         :
                         : "memory");
    return ((uint64_t)hi << 32) | lo;
}

static inline uint64_t
rdtsc_end(void)
{
    unsigned lo;
    unsigned hi;
    __asm__ __volatile__("rdtscp\n\t"
                         "lfence\n\t"
                         : "=a"(lo), "=d"(hi)
                         :
                         : "rcx", "memory");
    return ((uint64_t)hi << 32) | lo;
}

static uint64_t
xorshift64(uint64_t *state)
{
    uint64_t value = *state;
    value ^= value << 13;
    value ^= value >> 7;
    value ^= value << 17;
    *state = value;
    return value;
}

int
main(int argc, char **argv)
{
    if (argc < 4 || argc > 5) {
        usage(argv[0]);
    }

    const long node_long = parse_long_arg(argv[1], "node");
    const long latency_mib_long = parse_long_arg(argv[2], "latency_MiB");
    const uint64_t latency_iterations =
        parse_u64_arg(argv[3], "latency_iterations");
    double cpu_mhz = 2100.0;
    if (argc >= 5) {
        cpu_mhz = parse_double_arg(argv[4], "cpu_mhz");
    }

    if (node_long < 0 || latency_mib_long <= 0 || latency_iterations == 0 ||
        cpu_mhz <= 0.0) {
        usage(argv[0]);
    }

    const int node = (int)node_long;
    const size_t latency_bytes =
        (size_t)latency_mib_long * 1024UL * 1024UL;
    if ((latency_bytes % CACHELINE_BYTES) != 0) {
        fprintf(stderr, "latency buffer must be cacheline aligned in size\n");
        return 2;
    }

    uintptr_t *buffer = NULL;
    if (posix_memalign((void **)&buffer, CACHELINE_BYTES, latency_bytes) != 0) {
        perror("posix_memalign");
        return 1;
    }

    const size_t stride_words = CACHELINE_BYTES / sizeof(uintptr_t);
    const size_t lines = latency_bytes / CACHELINE_BYTES;
    size_t *order = malloc(lines * sizeof(*order));
    if (order == NULL) {
        perror("malloc");
        free(buffer);
        return 1;
    }

    for (size_t i = 0; i < lines; ++i) {
        order[i] = i;
    }

    uint64_t rng_state = 0x9e3779b97f4a7c15ULL;
    for (size_t i = lines - 1; i > 0; --i) {
        const size_t j = (size_t)(xorshift64(&rng_state) % (i + 1));
        const size_t tmp = order[i];
        order[i] = order[j];
        order[j] = tmp;
    }

    memset(buffer, 0, latency_bytes);
    for (size_t i = 0; i < lines; ++i) {
        const size_t cur = order[i];
        const size_t nxt = order[(i + 1) % lines];
        buffer[cur * stride_words] =
            (uintptr_t)&buffer[nxt * stride_words];
    }

    uintptr_t *cursor = &buffer[order[0] * stride_words];
    for (size_t i = 0; i < lines; ++i) {
        cursor = (uintptr_t *)(*cursor);
    }

    enter_roi();

    const uint64_t start = rdtsc_begin();
    for (uint64_t i = 0; i < latency_iterations; ++i) {
        cursor = (uintptr_t *)(*cursor);
    }
    const uint64_t end = rdtsc_end();
    const uint64_t total_cycles = end - start;

    __asm__ __volatile__("" : : "r"(cursor) : "memory");

    const double latency_cycles =
        (double)total_cycles / (double)latency_iterations;
    const double latency_ns = latency_cycles * 1000.0 / cpu_mhz;

    printf("LAT_RESULT node=%d latency_ns=%.3f latency_cycles=%.3f "
           "latency_mib=%ld latency_iters=%" PRIu64 " cpu_mhz=%.3f\n",
           node, latency_ns, latency_cycles, latency_mib_long,
           latency_iterations, cpu_mhz);

    free(order);
    free(buffer);
    return 0;
}
