// Copyright (c) 2026
// SPDX-License-Identifier: BSD-3-Clause

#include <algorithm>
#include <cmath>
#include <cstdint>
#include <cstdlib>
#include <cstring>
#include <fstream>
#include <iostream>
#include <numeric>
#include <string>
#include <vector>

#ifdef _OPENMP
#include <omp.h>
#endif

namespace {

struct Options {
    int scale = 16;
    int trials = 1;
    int max_iters = 20;
    double tolerance = 1e-4;
    bool no_roi = false;
    std::string file;
};

struct Graph {
    std::vector<uint64_t> row_start;
    std::vector<uint32_t> in_neighbors;
    std::vector<uint32_t> out_degree;
};

void usage(const char *name) {
    std::cerr
        << "Usage: " << name << " [-g scale] [-n trials] [-i iters] "
        << "[-t tolerance] [-f graph.sg] [--no-roi]\n";
}

Options parse_args(int argc, char **argv) {
    Options opts;
    for (int i = 1; i < argc; ++i) {
        const std::string arg(argv[i]);
        auto need_value = [&](const char *flag) -> const char * {
            if (i + 1 >= argc) {
                std::cerr << "missing value for " << flag << "\n";
                usage(argv[0]);
                std::exit(2);
            }
            return argv[++i];
        };

        if (arg == "-g") {
            opts.scale = std::atoi(need_value("-g"));
        } else if (arg == "-n") {
            opts.trials = std::atoi(need_value("-n"));
        } else if (arg == "-i") {
            opts.max_iters = std::atoi(need_value("-i"));
        } else if (arg == "-t") {
            opts.tolerance = std::atof(need_value("-t"));
        } else if (arg == "-f") {
            opts.file = need_value("-f");
        } else if (arg == "--no-roi") {
            opts.no_roi = true;
        } else if (arg == "-h" || arg == "--help") {
            usage(argv[0]);
            std::exit(0);
        } else {
            std::cerr << "unknown argument: " << arg << "\n";
            usage(argv[0]);
            std::exit(2);
        }
    }

    if (opts.scale <= 0 || opts.scale > 31) {
        std::cerr << "-g scale must be in [1, 31]\n";
        std::exit(2);
    }
    if (opts.trials <= 0 || opts.max_iters <= 0) {
        std::cerr << "-n and -i must be positive\n";
        std::exit(2);
    }
    return opts;
}

uint64_t splitmix64(uint64_t x) {
    x += 0x9e3779b97f4a7c15ULL;
    x = (x ^ (x >> 30)) * 0xbf58476d1ce4e5b9ULL;
    x = (x ^ (x >> 27)) * 0x94d049bb133111ebULL;
    return x ^ (x >> 31);
}

Graph make_graph(int scale) {
    const uint32_t vertices = uint32_t{1} << scale;
    const uint32_t edges_per_vertex = 16;
    const uint64_t edges = uint64_t(vertices) * edges_per_vertex;

    std::vector<std::vector<uint32_t> > incoming(vertices);
    std::vector<uint32_t> out_degree(vertices, edges_per_vertex);
    for (uint32_t src = 0; src < vertices; ++src) {
        for (uint32_t edge = 0; edge < edges_per_vertex; ++edge) {
            const uint64_t mixed =
                splitmix64((uint64_t(src) << 32) | uint64_t(edge));
            uint32_t dst = uint32_t(mixed & (vertices - 1));
            if (dst == src) {
                dst = (dst + 1) & (vertices - 1);
            }
            incoming[dst].push_back(src);
        }
    }

    Graph graph;
    graph.row_start.resize(uint64_t(vertices) + 1);
    graph.in_neighbors.reserve(edges);
    graph.out_degree.swap(out_degree);

    uint64_t offset = 0;
    for (uint32_t v = 0; v < vertices; ++v) {
        graph.row_start[v] = offset;
        graph.in_neighbors.insert(
            graph.in_neighbors.end(), incoming[v].begin(), incoming[v].end());
        offset = graph.in_neighbors.size();
    }
    graph.row_start[vertices] = offset;
    return graph;
}

template <typename T>
void read_exact(std::ifstream *file, T *value, const char *label) {
    file->read(reinterpret_cast<char *>(value), sizeof(T));
    if (!*file) {
        std::cerr << "failed reading " << label << "\n";
        std::exit(2);
    }
}

template <typename T>
void read_vector(std::ifstream *file, std::vector<T> *values, const char *label) {
    if (values->empty()) {
        return;
    }
    file->read(
        reinterpret_cast<char *>(values->data()),
        std::streamsize(values->size() * sizeof(T)));
    if (!*file) {
        std::cerr << "failed reading " << label << "\n";
        std::exit(2);
    }
}

Graph load_serialized_graph(const std::string &path) {
    if (path.size() < 3 || path.substr(path.size() - 3) != ".sg") {
        std::cerr << "only GAPBS .sg serialized graphs are supported by -f\n";
        std::exit(2);
    }

    std::ifstream file(path.c_str(), std::ios::binary);
    if (!file.is_open()) {
        std::cerr << "could not open graph file: " << path << "\n";
        std::exit(2);
    }

    bool directed = false;
    int64_t num_edges = 0;
    int64_t num_nodes = 0;
    read_exact(&file, &directed, "directed flag");
    read_exact(&file, &num_edges, "edge count");
    read_exact(&file, &num_nodes, "node count");
    if (num_nodes <= 0 || num_edges < 0) {
        std::cerr << "invalid serialized graph sizes\n";
        std::exit(2);
    }

    std::vector<int64_t> out_offsets(static_cast<size_t>(num_nodes) + 1);
    std::vector<int32_t> out_neighbors(static_cast<size_t>(num_edges));
    read_vector(&file, &out_offsets, "out offsets");
    read_vector(&file, &out_neighbors, "out neighbors");

    Graph graph;
    graph.out_degree.resize(size_t(num_nodes));
    for (size_t v = 0; v < size_t(num_nodes); ++v) {
        graph.out_degree[v] = uint32_t(out_offsets[v + 1] - out_offsets[v]);
        if (graph.out_degree[v] == 0) {
            graph.out_degree[v] = 1;
        }
    }

    std::vector<int64_t> in_offsets;
    std::vector<int32_t> in_neighbors;
    if (directed) {
        in_offsets.resize(size_t(num_nodes) + 1);
        in_neighbors.resize(size_t(num_edges));
        read_vector(&file, &in_offsets, "in offsets");
        read_vector(&file, &in_neighbors, "in neighbors");
    } else {
        in_offsets.swap(out_offsets);
        in_neighbors.swap(out_neighbors);
    }

    graph.row_start.resize(size_t(num_nodes) + 1);
    graph.in_neighbors.resize(in_neighbors.size());
    for (size_t i = 0; i < graph.row_start.size(); ++i) {
        graph.row_start[i] = uint64_t(in_offsets[i]);
    }
    for (size_t i = 0; i < graph.in_neighbors.size(); ++i) {
        graph.in_neighbors[i] = uint32_t(in_neighbors[i]);
    }
    return graph;
}

double wall_seconds() {
#ifdef _OPENMP
    return omp_get_wtime();
#else
    return 0.0;
#endif
}

double pagerank_spmv_trial(
    const Graph &graph,
    int max_iters,
    double tolerance,
    std::vector<double> *scores_out) {
    const size_t vertices = graph.row_start.size() - 1;
    const double init_score = 1.0 / double(vertices);
    const double base_score = (1.0 - 0.85) / double(vertices);
    std::vector<double> scores(vertices, init_score);
    std::vector<double> outgoing_contrib(vertices, 0.0);
    std::vector<double> next(vertices, 0.0);

    const double start = wall_seconds();
    for (int iter = 0; iter < max_iters; ++iter) {
#pragma omp parallel for schedule(static)
        for (size_t v = 0; v < vertices; ++v) {
            outgoing_contrib[v] = scores[v] / double(graph.out_degree[v]);
        }

        double error = 0.0;
#pragma omp parallel for schedule(dynamic, 64) reduction(+ : error)
        for (size_t v = 0; v < vertices; ++v) {
            double incoming_total = 0.0;
            for (uint64_t offset = graph.row_start[v];
                 offset < graph.row_start[v + 1];
                 ++offset) {
                incoming_total += outgoing_contrib[graph.in_neighbors[offset]];
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

void enter_roi_if_needed(bool no_roi) {
    if (!no_roi) {
        const int status = std::system("gem5-bridge hypercall 4");
        if (status != 0) {
            std::cerr << "warning: ROI hypercall command exited with status "
                      << status << "\n";
        }
    }
}

} // namespace

int main(int argc, char **argv) {
    const Options opts = parse_args(argc, argv);
#ifdef _OPENMP
    if (omp_get_max_threads() != 1) {
        omp_set_num_threads(1);
    }
#endif

    std::cout << "STEP16_CONFIG scale=" << opts.scale
              << " trials=" << opts.trials
              << " max_iters=" << opts.max_iters
              << " tolerance=" << opts.tolerance
              << " no_roi=" << (opts.no_roi ? 1 : 0) << "\n";

    Graph graph = opts.file.empty() ? make_graph(opts.scale)
                                    : load_serialized_graph(opts.file);
    const size_t vertices = graph.row_start.size() - 1;
    std::cout << "STEP16_GRAPH vertices=" << vertices
              << " directed_edges=" << graph.in_neighbors.size() << "\n";

    enter_roi_if_needed(opts.no_roi);

    for (int trial = 0; trial < opts.trials; ++trial) {
        std::vector<double> scores;
        const double seconds =
            pagerank_spmv_trial(graph, opts.max_iters, opts.tolerance, &scores);
        const double checksum =
            std::accumulate(scores.begin(), scores.end(), 0.0);
        std::cout << "STEP16_TRIAL trial=" << trial
                  << " seconds=" << seconds
                  << " checksum=" << checksum << "\n";
    }

    return 0;
}
