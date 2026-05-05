// Copyright (c) 2026
// SPDX-License-Identifier: BSD-3-Clause

#include "gapbs_roi_common.hh"

uint64_t count_intersection(
    const std::vector<uint32_t> &neighbors,
    uint64_t a_begin,
    uint64_t a_end,
    uint64_t b_begin,
    uint64_t b_end) {
    uint64_t count = 0;
    while (a_begin < a_end && b_begin < b_end) {
        const uint32_t a = neighbors[a_begin];
        const uint32_t b = neighbors[b_begin];
        if (a == b) {
            ++count;
            ++a_begin;
            ++b_begin;
        } else if (a < b) {
            ++a_begin;
        } else {
            ++b_begin;
        }
    }
    return count;
}

double tc_trial(const Graph &graph, uint64_t *triangles_out) {
    const size_t vertices = graph.out_degree.size();
    uint64_t triangles = 0;
    const double start = wall_seconds();
#pragma omp parallel for schedule(dynamic, 16) reduction(+ : triangles)
    for (size_t v = 0; v < vertices; ++v) {
        const uint64_t v_begin = graph.out_row_start[v];
        const uint64_t v_end = graph.out_row_start[v + 1];
        for (uint64_t offset = v_begin; offset < v_end; ++offset) {
            const uint32_t u = graph.out_neighbors[offset];
            if (u <= v) {
                continue;
            }
            triangles += count_intersection(
                graph.out_neighbors,
                v_begin,
                v_end,
                graph.out_row_start[u],
                graph.out_row_start[u + 1]);
        }
    }
    const double elapsed = wall_seconds() - start;
    *triangles_out = triangles;
    return elapsed;
}

int main(int argc, char **argv) {
    const Options opts = parse_args(argc, argv);
    print_config("tc", opts);

    Graph graph = opts.file.empty() ? make_graph(opts.scale)
                                    : load_serialized_graph(opts.file);
    print_graph(graph);

    enter_roi_if_needed(opts.no_roi);
    for (int trial = 0; trial < opts.trials; ++trial) {
        uint64_t triangles = 0;
        const double seconds = tc_trial(graph, &triangles);
        std::cout << "STEP16_TRIAL trial=" << trial
                  << " seconds=" << seconds
                  << " checksum=" << triangles << "\n";
    }
    exit_roi_if_needed(opts.no_roi);
    return 0;
}
