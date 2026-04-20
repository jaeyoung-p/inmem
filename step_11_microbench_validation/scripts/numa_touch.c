// Copyright (c) 2026
// SPDX-License-Identifier: BSD-3-Clause

#define _GNU_SOURCE

#include <errno.h>
#include <inttypes.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/mman.h>
#include <sys/syscall.h>
#include <time.h>
#include <unistd.h>

#ifndef MPOL_BIND
#define MPOL_BIND 2
#endif

#define CACHE_LINE_BYTES 64UL

static double
seconds_now(void)
{
    struct timespec ts;
    if (clock_gettime(CLOCK_MONOTONIC, &ts) != 0) {
        perror("clock_gettime");
        exit(1);
    }
    return (double)ts.tv_sec + (double)ts.tv_nsec / 1000000000.0;
}

static void
usage(const char *prog)
{
    fprintf(stderr,
            "usage: %s <node> <MiB> <passes> <bench> [stride_bytes]\n"
            "benches: read_seq write_seq readwrite_seq read_stride chase\n",
            prog);
    exit(2);
}

static uint64_t
xorshift64(uint64_t *state)
{
    uint64_t x = *state;
    x ^= x << 13;
    x ^= x >> 7;
    x ^= x << 17;
    *state = x;
    return x;
}

static void
first_touch(uint8_t *buf, size_t length, size_t page_size)
{
    for (size_t offset = 0; offset < length; offset += page_size) {
        buf[offset] = (uint8_t)(offset >> 12);
    }
}

static double
run_read_seq(volatile uint8_t *buf, size_t length, long passes,
             uint64_t *checksum, uint64_t *ops)
{
    const double start = seconds_now();
    for (long pass = 0; pass < passes; pass++) {
        for (size_t offset = 0; offset < length; offset += CACHE_LINE_BYTES) {
            *checksum += buf[offset];
            *ops += 1;
        }
    }
    return seconds_now() - start;
}

static double
run_write_seq(volatile uint8_t *buf, size_t length, long passes,
              uint64_t *checksum, uint64_t *ops)
{
    const double start = seconds_now();
    for (long pass = 0; pass < passes; pass++) {
        for (size_t offset = 0; offset < length; offset += CACHE_LINE_BYTES) {
            buf[offset] = (uint8_t)(offset + (size_t)pass);
            *ops += 1;
        }
    }
    *checksum += buf[(length - CACHE_LINE_BYTES) & ~(CACHE_LINE_BYTES - 1)];
    return seconds_now() - start;
}

static double
run_readwrite_seq(volatile uint8_t *buf, size_t length, long passes,
                  uint64_t *checksum, uint64_t *ops)
{
    const double start = seconds_now();
    for (long pass = 0; pass < passes; pass++) {
        for (size_t offset = 0; offset < length; offset += CACHE_LINE_BYTES) {
            const uint8_t value = (uint8_t)(buf[offset] + 1U);
            buf[offset] = value;
            *checksum += value;
            *ops += 1;
        }
    }
    return seconds_now() - start;
}

static double
run_read_stride(volatile uint8_t *buf, size_t length, long passes,
                size_t stride, uint64_t *checksum, uint64_t *ops)
{
    const double start = seconds_now();
    for (long pass = 0; pass < passes; pass++) {
        for (size_t offset = 0; offset < length; offset += stride) {
            *checksum += buf[offset];
            *ops += 1;
        }
    }
    return seconds_now() - start;
}

static double
run_chase(uint8_t *buf, size_t length, long passes, uint64_t *checksum,
          uint64_t *ops)
{
    const size_t lines = length / CACHE_LINE_BYTES;
    if (lines < 2 || lines > UINT32_MAX) {
        fprintf(stderr, "chase needs between 2 and %" PRIu32 " cache lines\n",
                UINT32_MAX);
        exit(2);
    }

    uint32_t *order = malloc(lines * sizeof(*order));
    if (order == NULL) {
        perror("malloc");
        exit(1);
    }

    for (size_t i = 0; i < lines; i++) {
        order[i] = (uint32_t)i;
    }

    uint64_t rng = 0x9e3779b97f4a7c15ULL ^ (uint64_t)length;
    for (size_t i = lines - 1; i > 0; i--) {
        const size_t j = xorshift64(&rng) % (i + 1);
        const uint32_t tmp = order[i];
        order[i] = order[j];
        order[j] = tmp;
    }

    for (size_t i = 0; i < lines; i++) {
        const uint32_t here = order[i];
        const uint32_t next = order[(i + 1) % lines];
        uint32_t *slot = (uint32_t *)(void *)(buf + here * CACHE_LINE_BYTES);
        *slot = next;
    }

    uint32_t idx = order[0];
    const volatile uint8_t *vbuf = buf;
    const uint64_t iterations = (uint64_t)passes * (uint64_t)lines;
    const double start = seconds_now();
    for (uint64_t iter = 0; iter < iterations; iter++) {
        const volatile uint32_t *slot =
            (const volatile uint32_t *)(vbuf + idx * CACHE_LINE_BYTES);
        idx = *slot;
    }
    const double elapsed = seconds_now() - start;

    *checksum += idx;
    *ops += iterations;
    free(order);
    return elapsed;
}

int
main(int argc, char **argv)
{
    if (argc != 5 && argc != 6) {
        usage(argv[0]);
    }

    const long node = strtol(argv[1], NULL, 0);
    const long mib = strtol(argv[2], NULL, 0);
    const long passes = strtol(argv[3], NULL, 0);
    const char *bench = argv[4];
    if (node < 0 || node >= (long)(8 * sizeof(unsigned long)) ||
        mib <= 0 || passes <= 0) {
        usage(argv[0]);
    }

    const long page_size_long = sysconf(_SC_PAGESIZE);
    if (page_size_long <= 0) {
        perror("sysconf(_SC_PAGESIZE)");
        return 1;
    }
    const size_t page_size = (size_t)page_size_long;
    size_t stride = page_size;
    if (argc == 6) {
        const long parsed_stride = strtol(argv[5], NULL, 0);
        if (parsed_stride <= 0) {
            usage(argv[0]);
        }
        stride = (size_t)parsed_stride;
    }
    if (stride < CACHE_LINE_BYTES) {
        stride = CACHE_LINE_BYTES;
    }

    const size_t length = (size_t)mib * 1024UL * 1024UL;
    uint8_t *buf = mmap(NULL, length, PROT_READ | PROT_WRITE,
                        MAP_PRIVATE | MAP_ANONYMOUS, -1, 0);
    if (buf == MAP_FAILED) {
        perror("mmap");
        return 1;
    }

    unsigned long nodemask = 1UL << node;
    const unsigned long maxnode = 8UL * (unsigned long)sizeof(nodemask);
    const long mbind_ret = syscall(SYS_mbind, buf, length, MPOL_BIND,
                                   &nodemask, maxnode, 0);
    if (mbind_ret != 0) {
        fprintf(stderr,
                "MB_WARN mbind node %ld failed: %s; continuing with "
                "caller-supplied NUMA policy\n",
                node, strerror(errno));
    }

    first_touch(buf, length, page_size);

    uint64_t checksum = 0;
    uint64_t ops = 0;
    double elapsed = 0.0;
    if (strcmp(bench, "read_seq") == 0) {
        elapsed = run_read_seq(buf, length, passes, &checksum, &ops);
    } else if (strcmp(bench, "write_seq") == 0) {
        elapsed = run_write_seq(buf, length, passes, &checksum, &ops);
    } else if (strcmp(bench, "readwrite_seq") == 0) {
        elapsed = run_readwrite_seq(buf, length, passes, &checksum, &ops);
    } else if (strcmp(bench, "read_stride") == 0) {
        elapsed = run_read_stride(buf, length, passes, stride, &checksum, &ops);
    } else if (strcmp(bench, "chase") == 0) {
        elapsed = run_chase(buf, length, passes, &checksum, &ops);
    } else {
        usage(argv[0]);
    }

    const double ns_per_op = elapsed * 1000000000.0 / (double)ops;
    const double bytes_touched =
        strcmp(bench, "read_stride") == 0 ? (double)ops * CACHE_LINE_BYTES :
        strcmp(bench, "chase") == 0 ? (double)ops * CACHE_LINE_BYTES :
        (double)mib * 1024.0 * 1024.0 * (double)passes;
    const double bandwidth_mib_s = bytes_touched / (1024.0 * 1024.0) / elapsed;

    printf("MB_RESULT node=%ld bench=%s mib=%ld passes=%ld stride=%zu "
           "seconds=%.9f ops=%" PRIu64 " ns_per_op=%.3f "
           "bandwidth_mib_s=%.3f checksum=%" PRIu64 "\n",
           node, bench, mib, passes, stride, elapsed, ops, ns_per_op,
           bandwidth_mib_s, checksum);

    munmap(buf, length);
    return 0;
}
