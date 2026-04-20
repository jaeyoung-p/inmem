// Copyright (c) 2026
// SPDX-License-Identifier: BSD-3-Clause

#define _GNU_SOURCE

#include <errno.h>
#include <inttypes.h>
#include <pthread.h>
#include <sched.h>
#include <stdatomic.h>
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

struct worker_state
{
    int index;
    int cpu;
    volatile uint8_t *buf;
    size_t length;
    pthread_barrier_t *barrier;
    atomic_int *stop;
    uint64_t bytes;
    uint64_t checksum;
};

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

static uint64_t
cycles_now(void)
{
    uint32_t lo;
    uint32_t hi;
    __asm__ __volatile__("lfence\n\t"
                         "rdtsc\n\t"
                         : "=a"(lo), "=d"(hi)
                         :
                         : "memory");
    return ((uint64_t)hi << 32) | (uint64_t)lo;
}

static void
usage(const char *prog)
{
    fprintf(stderr,
            "usage: %s <node> <max_workers> <worker_MiB> <latency_MiB> "
            "<latency_iterations> [worker_step] [cpu_mhz]\n",
            prog);
    exit(2);
}

static long
parse_long_arg(const char *text, const char *name)
{
    char *end = NULL;
    errno = 0;
    const long value = strtol(text, &end, 0);
    if (errno != 0 || end == text || *end != '\0') {
        fprintf(stderr, "invalid %s: %s\n", name, text);
        exit(2);
    }
    return value;
}

static uint64_t
parse_u64_arg(const char *text, const char *name)
{
    char *end = NULL;
    errno = 0;
    const unsigned long long value = strtoull(text, &end, 0);
    if (errno != 0 || end == text || *end != '\0') {
        fprintf(stderr, "invalid %s: %s\n", name, text);
        exit(2);
    }
    return (uint64_t)value;
}

static double
parse_double_arg(const char *text, const char *name)
{
    char *end = NULL;
    errno = 0;
    const double value = strtod(text, &end);
    if (errno != 0 || end == text || *end != '\0') {
        fprintf(stderr, "invalid %s: %s\n", name, text);
        exit(2);
    }
    return value;
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
bind_to_cpu(int cpu, const char *who)
{
    cpu_set_t set;
    CPU_ZERO(&set);
    CPU_SET(cpu, &set);

    if (sched_setaffinity(0, sizeof(set), &set) != 0) {
        fprintf(stderr, "BWL_WARN sched_setaffinity cpu %d for %s failed: %s\n",
                cpu, who, strerror(errno));
    }
}

static void
first_touch(uint8_t *buf, size_t length)
{
    const long page_size_long = sysconf(_SC_PAGESIZE);
    if (page_size_long <= 0) {
        perror("sysconf(_SC_PAGESIZE)");
        exit(1);
    }

    const size_t page_size = (size_t)page_size_long;
    for (size_t offset = 0; offset < length; offset += page_size) {
        buf[offset] = (uint8_t)(offset >> 12);
    }
}

static uint8_t *
alloc_on_node(int node, size_t length, const char *name)
{
    uint8_t *buf = mmap(NULL, length, PROT_READ | PROT_WRITE,
                        MAP_PRIVATE | MAP_ANONYMOUS, -1, 0);
    if (buf == MAP_FAILED) {
        fprintf(stderr, "mmap %s failed: %s\n", name, strerror(errno));
        exit(1);
    }

    if (node < 0 || node >= (int)(8 * sizeof(unsigned long))) {
        fprintf(stderr, "node %d does not fit in the local mbind nodemask\n",
                node);
        exit(2);
    }

    unsigned long nodemask = 1UL << node;
    const unsigned long maxnode = 8UL * (unsigned long)sizeof(nodemask);
    if (syscall(SYS_mbind, buf, length, MPOL_BIND, &nodemask, maxnode, 0) !=
        0) {
        fprintf(stderr,
                "BWL_WARN mbind %s to node %d failed: %s; continuing with "
                "caller-supplied NUMA policy\n",
                name, node, strerror(errno));
    }

    first_touch(buf, length);
    return buf;
}

static void
prepare_chase(uint8_t *buf, size_t length)
{
    const size_t lines = length / CACHE_LINE_BYTES;
    if (lines < 2 || lines > UINT32_MAX) {
        fprintf(stderr, "latency buffer needs between 2 and %" PRIu32
                " cache lines\n",
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

    uint64_t rng = 0x6a09e667f3bcc909ULL ^ (uint64_t)length;
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

    free(order);
}

static uint64_t
run_chase(volatile uint8_t *buf, uint64_t iterations)
{
    uint32_t idx = 0;
    for (uint64_t iter = 0; iter < iterations; iter++) {
        const volatile uint32_t *slot =
            (const volatile uint32_t *)(buf + (size_t)idx * CACHE_LINE_BYTES);
        idx = *slot;
    }
    return idx;
}

static void *
worker_main(void *arg)
{
    struct worker_state *state = arg;
    char who[32];
    snprintf(who, sizeof(who), "worker-%d", state->index);
    bind_to_cpu(state->cpu, who);

    pthread_barrier_wait(state->barrier);

    uint64_t bytes = 0;
    uint64_t checksum = 0;
    while (atomic_load_explicit(state->stop, memory_order_relaxed) == 0) {
        for (size_t offset = 0; offset < state->length;
             offset += CACHE_LINE_BYTES) {
            checksum += state->buf[offset];
            bytes += CACHE_LINE_BYTES;
        }
    }

    state->bytes = bytes;
    state->checksum = checksum;
    return NULL;
}

static void
run_point(int node, int workers, size_t worker_length, size_t latency_length,
          uint64_t latency_iterations, double cpu_mhz)
{
    uint8_t *latency_buf = alloc_on_node(node, latency_length, "latency");
    prepare_chase(latency_buf, latency_length);

    pthread_t *threads = NULL;
    struct worker_state *states = NULL;
    uint8_t **worker_bufs = NULL;
    pthread_barrier_t barrier;
    atomic_int stop;
    atomic_init(&stop, 0);

    if (workers > 0) {
        threads = calloc((size_t)workers, sizeof(*threads));
        states = calloc((size_t)workers, sizeof(*states));
        worker_bufs = calloc((size_t)workers, sizeof(*worker_bufs));
        if (threads == NULL || states == NULL || worker_bufs == NULL) {
            perror("calloc workers");
            exit(1);
        }

        for (int i = 0; i < workers; i++) {
            worker_bufs[i] = alloc_on_node(node, worker_length, "worker");
        }

        if (pthread_barrier_init(&barrier, NULL, (unsigned int)workers + 1) !=
            0) {
            perror("pthread_barrier_init");
            exit(1);
        }

        for (int i = 0; i < workers; i++) {
            states[i].index = i;
            states[i].cpu = i + 1;
            states[i].buf = worker_bufs[i];
            states[i].length = worker_length;
            states[i].barrier = &barrier;
            states[i].stop = &stop;
            const int ret = pthread_create(&threads[i], NULL, worker_main,
                                           &states[i]);
            if (ret != 0) {
                fprintf(stderr, "pthread_create worker %d failed: %s\n", i,
                        strerror(ret));
                exit(1);
            }
        }
    }

    bind_to_cpu(0, "latency");
    if (workers > 0) {
        pthread_barrier_wait(&barrier);
    }

    const double clock_start = seconds_now();
    const uint64_t cycle_start = cycles_now();
    const uint64_t latency_checksum = run_chase(latency_buf,
                                                latency_iterations);
    const uint64_t cycle_end = cycles_now();
    const double clock_elapsed = seconds_now() - clock_start;
    const uint64_t elapsed_cycles = cycle_end - cycle_start;

    atomic_store_explicit(&stop, 1, memory_order_relaxed);

    uint64_t worker_bytes = 0;
    uint64_t worker_checksum = 0;
    for (int i = 0; i < workers; i++) {
        pthread_join(threads[i], NULL);
        worker_bytes += states[i].bytes;
        worker_checksum += states[i].checksum;
    }

    const double elapsed =
        (double)elapsed_cycles / (cpu_mhz * 1000000.0);
    const double safe_elapsed = elapsed > 0.0 ? elapsed : 1e-12;
    const double bandwidth_mib_s =
        (double)worker_bytes / (1024.0 * 1024.0) / safe_elapsed;
    const double latency_ns =
        safe_elapsed * 1000000000.0 / (double)latency_iterations;
    const uint64_t checksum = latency_checksum ^ worker_checksum;

    printf("BWL_RESULT node=%d workers=%d worker_mib=%zu latency_mib=%zu "
           "latency_iters=%" PRIu64 " cpu_mhz=%.3f cycles=%" PRIu64
           " seconds=%.9f clock_seconds=%.9f worker_bytes=%" PRIu64
           " bandwidth_mib_s=%.3f latency_ns=%.3f checksum=%" PRIu64 "\n",
           node, workers, worker_length / (1024UL * 1024UL),
           latency_length / (1024UL * 1024UL), latency_iterations, cpu_mhz,
           elapsed_cycles, elapsed, clock_elapsed, worker_bytes,
           bandwidth_mib_s, latency_ns, checksum);
    fflush(stdout);

    if (workers > 0) {
        pthread_barrier_destroy(&barrier);
        for (int i = 0; i < workers; i++) {
            munmap(worker_bufs[i], worker_length);
        }
    }
    munmap(latency_buf, latency_length);
    free(worker_bufs);
    free(states);
    free(threads);
}

int
main(int argc, char **argv)
{
    if (argc < 6 || argc > 8) {
        usage(argv[0]);
    }

    const long node_long = parse_long_arg(argv[1], "node");
    const long max_workers_long = parse_long_arg(argv[2], "max_workers");
    const long worker_mib_long = parse_long_arg(argv[3], "worker_MiB");
    const long latency_mib_long = parse_long_arg(argv[4], "latency_MiB");
    const uint64_t latency_iterations =
        parse_u64_arg(argv[5], "latency_iterations");
    long worker_step_long = 1;
    if (argc >= 7) {
        worker_step_long = parse_long_arg(argv[6], "worker_step");
    }
    double cpu_mhz = 3000.0;
    if (argc >= 8) {
        cpu_mhz = parse_double_arg(argv[7], "cpu_mhz");
    }

    if (node_long < 0 || max_workers_long < 0 || worker_mib_long <= 0 ||
        latency_mib_long <= 0 || latency_iterations == 0 ||
        worker_step_long <= 0 || cpu_mhz <= 0.0) {
        usage(argv[0]);
    }

    const int node = (int)node_long;
    const int max_workers = (int)max_workers_long;
    const int worker_step = (int)worker_step_long;
    const size_t worker_length =
        (size_t)worker_mib_long * 1024UL * 1024UL;
    const size_t latency_length =
        (size_t)latency_mib_long * 1024UL * 1024UL;

    for (int workers = 0; workers <= max_workers;) {
        run_point(node, workers, worker_length, latency_length,
                  latency_iterations, cpu_mhz);
        if (workers == max_workers) {
            break;
        }
        workers += worker_step;
        if (workers > max_workers) {
            workers = max_workers;
        }
    }

    return 0;
}
