// Copyright (c) 2026
// SPDX-License-Identifier: BSD-3-Clause

#include "gapbs_roi_common.hh"

double sssp_trial(
    const Graph &graph,
    int max_iters,
    int trial,
    uint64_t *checksum_out) {
    const size_t vertices = graph.out_degree.size();
    const uint32_t inf = UINT32_MAX / 4;
    std::vector<uint32_t> distance(vertices, inf);
    std::vector<uint32_t> next(vertices, inf);
    distance[choose_source(vertices, trial)] = 0;

    const double start = wall_seconds();
    for (int iter = 0; iter < max_iters; ++iter) {
        int changed = 0;
#pragma omp parallel for schedule(dynamic, 64) reduction(+ : changed)
        for (size_t v = 0; v < vertices; ++v) {
            uint32_t best = distance[v];
            for (uint64_t offset = graph.in_row_start[v];
                 offset < graph.in_row_start[v + 1];
                 ++offset) {
                const uint32_t src = graph.in_neighbors[offset];
                const uint32_t weight = 1 + ((uint32_t(src) ^ uint32_t(v)) & 7);
                const uint32_t candidate = distance[src] + weight;
                if (candidate < best) {
                    best = candidate;
                }
            }
            next[v] = best;
            changed += best != distance[v];
        }
        distance.swap(next);
        if (changed == 0) {
            break;
        }
    }
    const double elapsed = wall_seconds() - start;
    uint64_t checksum = 0;
    for (size_t v = 0; v < vertices; ++v) {
        checksum += distance[v] == inf ? 0 : distance[v];
    }
    *checksum_out = checksum;
    return elapsed;
}

int main(int argc, char **argv) {
    const Options opts = parse_args(argc, argv);
    print_config("sssp", opts);

    Graph graph = opts.file.empty() ? make_graph(opts.scale)
                                    : load_serialized_graph(opts.file);
    print_graph(graph);

    enter_roi_if_needed(opts.no_roi);
    for (int trial = 0; trial < opts.trials; ++trial) {
        uint64_t checksum = 0;
        const double seconds =
            sssp_trial(graph, opts.max_iters, trial, &checksum);
        std::cout << "STEP16_TRIAL trial=" << trial
                  << " seconds=" << seconds
                  << " checksum=" << checksum << "\n";
    }
    exit_roi_if_needed(opts.no_roi);
    return 0;
}
