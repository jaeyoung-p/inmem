// Copyright (c) 2026
// SPDX-License-Identifier: BSD-3-Clause

#include "gapbs_roi_common.hh"

double pagerank_trial(
    const Graph &graph,
    int max_iters,
    double tolerance,
    std::vector<double> *scores_out) {
    const size_t vertices = graph.in_row_start.size() - 1;
    const double init_score = 1.0 / double(vertices);
    const double base_score = (1.0 - 0.85) / double(vertices);
    std::vector<double> scores(vertices, init_score);
    std::vector<double> next(vertices, 0.0);

    const double start = wall_seconds();
    for (int iter = 0; iter < max_iters; ++iter) {
        double error = 0.0;
#pragma omp parallel for schedule(dynamic, 64) reduction(+ : error)
        for (size_t v = 0; v < vertices; ++v) {
            double incoming_total = 0.0;
            for (uint64_t offset = graph.in_row_start[v];
                 offset < graph.in_row_start[v + 1];
                 ++offset) {
                const uint32_t src = graph.in_neighbors[offset];
                incoming_total += scores[src] / double(graph.out_degree[src]);
            }
            const double score = base_score + 0.85 * incoming_total;
            next[v] = score;
            error += std::abs(score - scores[v]);
        }
        scores.swap(next);
        if (error < tolerance) {
            break;
        }
    }
    const double elapsed = wall_seconds() - start;
    scores_out->swap(scores);
    return elapsed;
}

int main(int argc, char **argv) {
    const Options opts = parse_args(argc, argv);
    print_config("pr", opts);

    Graph graph = opts.file.empty() ? make_graph(opts.scale)
                                    : load_serialized_graph(opts.file);
    print_graph(graph);

    enter_roi_if_needed(opts.no_roi);
    for (int trial = 0; trial < opts.trials; ++trial) {
        std::vector<double> scores;
        const double seconds =
            pagerank_trial(graph, opts.max_iters, opts.tolerance, &scores);
        const double checksum =
            std::accumulate(scores.begin(), scores.end(), 0.0);
        std::cout << "STEP16_TRIAL trial=" << trial
                  << " seconds=" << seconds
                  << " checksum=" << checksum << "\n";
    }
    exit_roi_if_needed(opts.no_roi);
    return 0;
}
