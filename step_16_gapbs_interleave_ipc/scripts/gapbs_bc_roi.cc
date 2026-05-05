// Copyright (c) 2026
// SPDX-License-Identifier: BSD-3-Clause

#include "gapbs_roi_common.hh"

double bc_trial(
    const Graph &graph,
    int max_iters,
    int trial,
    double *checksum_out) {
    const size_t vertices = graph.out_degree.size();
    const uint32_t source = choose_source(vertices, trial);
    std::vector<int32_t> depth(vertices, -1);
    std::vector<double> paths(vertices, 0.0);
    std::vector<double> dependency(vertices, 0.0);
    std::vector<uint32_t> frontier;
    std::vector<uint32_t> next_frontier;
    std::vector<uint32_t> levels;

    depth[source] = 0;
    paths[source] = 1.0;
    frontier.push_back(source);

    const double start = wall_seconds();
    for (int level = 0; !frontier.empty() && level < max_iters; ++level) {
        levels.insert(levels.end(), frontier.begin(), frontier.end());
        next_frontier.clear();
        for (size_t i = 0; i < frontier.size(); ++i) {
            const uint32_t v = frontier[i];
            for (uint64_t offset = graph.out_row_start[v];
                 offset < graph.out_row_start[v + 1];
                 ++offset) {
                const uint32_t dst = graph.out_neighbors[offset];
                if (depth[dst] < 0) {
                    depth[dst] = level + 1;
                    next_frontier.push_back(dst);
                }
                if (depth[dst] == level + 1) {
                    paths[dst] += paths[v];
                }
            }
        }
        frontier.swap(next_frontier);
    }

    for (std::vector<uint32_t>::reverse_iterator it = levels.rbegin();
         it != levels.rend();
         ++it) {
        const uint32_t v = *it;
        double sum = 0.0;
        for (uint64_t offset = graph.out_row_start[v];
             offset < graph.out_row_start[v + 1];
             ++offset) {
            const uint32_t dst = graph.out_neighbors[offset];
            if (depth[dst] == depth[v] + 1 && paths[dst] > 0.0) {
                sum += (paths[v] / paths[dst]) * (1.0 + dependency[dst]);
            }
        }
        dependency[v] += sum;
    }

    const double elapsed = wall_seconds() - start;
    *checksum_out = std::accumulate(dependency.begin(), dependency.end(), 0.0);
    return elapsed;
}

int main(int argc, char **argv) {
    const Options opts = parse_args(argc, argv);
    print_config("bc", opts);

    Graph graph = opts.file.empty() ? make_graph(opts.scale)
                                    : load_serialized_graph(opts.file);
    print_graph(graph);

    enter_roi_if_needed(opts.no_roi);
    for (int trial = 0; trial < opts.trials; ++trial) {
        double checksum = 0.0;
        const double seconds = bc_trial(graph, opts.max_iters, trial, &checksum);
        std::cout << "STEP16_TRIAL trial=" << trial
                  << " seconds=" << seconds
                  << " checksum=" << checksum << "\n";
    }
    exit_roi_if_needed(opts.no_roi);
    return 0;
}
