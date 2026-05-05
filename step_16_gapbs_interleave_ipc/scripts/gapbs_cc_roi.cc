// Copyright (c) 2026
// SPDX-License-Identifier: BSD-3-Clause

#include "gapbs_roi_common.hh"

double cc_trial(const Graph &graph, int max_iters, uint64_t *checksum_out) {
    const size_t vertices = graph.out_degree.size();
    std::vector<uint32_t> label(vertices);
    std::vector<uint32_t> next(vertices);
#pragma omp parallel for schedule(static)
    for (size_t v = 0; v < vertices; ++v) {
        label[v] = uint32_t(v);
        next[v] = uint32_t(v);
    }

    const double start = wall_seconds();
    for (int iter = 0; iter < max_iters; ++iter) {
        int changed = 0;
#pragma omp parallel for schedule(dynamic, 64) reduction(+ : changed)
        for (size_t v = 0; v < vertices; ++v) {
            uint32_t best = label[v];
            for (uint64_t offset = graph.out_row_start[v];
                 offset < graph.out_row_start[v + 1];
                 ++offset) {
                best = std::min(best, label[graph.out_neighbors[offset]]);
            }
            for (uint64_t offset = graph.in_row_start[v];
                 offset < graph.in_row_start[v + 1];
                 ++offset) {
                best = std::min(best, label[graph.in_neighbors[offset]]);
            }
            next[v] = best;
            changed += best != label[v];
        }
        label.swap(next);
        if (changed == 0) {
            break;
        }
    }
    const double elapsed = wall_seconds() - start;
    *checksum_out = std::accumulate(label.begin(), label.end(), uint64_t{0});
    return elapsed;
}

int main(int argc, char **argv) {
    const Options opts = parse_args(argc, argv);
    print_config("cc", opts);

    Graph graph = opts.file.empty() ? make_graph(opts.scale)
                                    : load_serialized_graph(opts.file);
    print_graph(graph);

    enter_roi_if_needed(opts.no_roi);
    for (int trial = 0; trial < opts.trials; ++trial) {
        uint64_t checksum = 0;
        const double seconds = cc_trial(graph, opts.max_iters, &checksum);
        std::cout << "STEP16_TRIAL trial=" << trial
                  << " seconds=" << seconds
                  << " checksum=" << checksum << "\n";
    }
    exit_roi_if_needed(opts.no_roi);
    return 0;
}
