// Copyright (c) 2026
// SPDX-License-Identifier: BSD-3-Clause

#ifndef STEP16_GAPBS_ROI_COMMON_HH
#define STEP16_GAPBS_ROI_COMMON_HH

#include <algorithm>
#include <cmath>
#include <cstdint>
#include <cstdlib>
#include <fstream>
#include <iostream>
#include <numeric>
#include <string>
#include <vector>

#ifdef _OPENMP
#include <omp.h>
#endif

struct Options {
    int scale = 16;
    int trials = 1;
    int max_iters = 20;
    double tolerance = 1e-4;
    bool no_roi = false;
    std::string file;
};

struct Graph {
    std::vector<uint64_t> in_row_start;
    std::vector<uint32_t> in_neighbors;
    std::vector<uint64_t> out_row_start;
    std::vector<uint32_t> out_neighbors;
    std::vector<uint32_t> out_degree;
};

inline void usage(const char *name) {
    std::cerr
        << "Usage: " << name << " [-g scale] [-n trials] [-i iters] "
        << "[-t tolerance] [-f graph.sg] [--no-roi]\n";
}

inline Options parse_args(int argc, char **argv) {
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

inline uint64_t splitmix64(uint64_t x) {
    x += 0x9e3779b97f4a7c15ULL;
    x = (x ^ (x >> 30)) * 0xbf58476d1ce4e5b9ULL;
    x = (x ^ (x >> 27)) * 0x94d049bb133111ebULL;
    return x ^ (x >> 31);
}

inline void fill_csr(
    const std::vector<std::vector<uint32_t> > &adj,
    std::vector<uint64_t> *row_start,
    std::vector<uint32_t> *neighbors) {
    row_start->resize(adj.size() + 1);
    uint64_t edges = 0;
    for (size_t v = 0; v < adj.size(); ++v) {
        (*row_start)[v] = edges;
        edges += adj[v].size();
    }
    (*row_start)[adj.size()] = edges;
    neighbors->clear();
    neighbors->reserve(edges);
    for (size_t v = 0; v < adj.size(); ++v) {
        neighbors->insert(neighbors->end(), adj[v].begin(), adj[v].end());
    }
}

inline Graph make_graph(int scale) {
    const uint32_t vertices = uint32_t{1} << scale;
    const uint32_t edges_per_vertex = 16;

    std::vector<std::vector<uint32_t> > incoming(vertices);
    std::vector<std::vector<uint32_t> > outgoing(vertices);
    for (uint32_t src = 0; src < vertices; ++src) {
        outgoing[src].reserve(edges_per_vertex);
        for (uint32_t edge = 0; edge < edges_per_vertex; ++edge) {
            const uint64_t mixed =
                splitmix64((uint64_t(src) << 32) | uint64_t(edge));
            uint32_t dst = uint32_t(mixed & (vertices - 1));
            if (dst == src) {
                dst = (dst + 1) & (vertices - 1);
            }
            outgoing[src].push_back(dst);
            incoming[dst].push_back(src);
        }
    }

    for (uint32_t v = 0; v < vertices; ++v) {
        std::sort(outgoing[v].begin(), outgoing[v].end());
        outgoing[v].erase(
            std::unique(outgoing[v].begin(), outgoing[v].end()),
            outgoing[v].end());
        std::sort(incoming[v].begin(), incoming[v].end());
        incoming[v].erase(
            std::unique(incoming[v].begin(), incoming[v].end()),
            incoming[v].end());
    }

    Graph graph;
    graph.out_degree.resize(vertices);
    for (uint32_t v = 0; v < vertices; ++v) {
        graph.out_degree[v] = std::max<size_t>(outgoing[v].size(), 1);
    }
    fill_csr(incoming, &graph.in_row_start, &graph.in_neighbors);
    fill_csr(outgoing, &graph.out_row_start, &graph.out_neighbors);
    return graph;
}

template <typename T>
inline void read_exact(std::ifstream *file, T *value, const char *label) {
    file->read(reinterpret_cast<char *>(value), sizeof(T));
    if (!*file) {
        std::cerr << "failed reading " << label << "\n";
        std::exit(2);
    }
}

template <typename T>
inline void read_vector(
    std::ifstream *file,
    std::vector<T> *values,
    const char *label) {
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

inline Graph load_serialized_graph(const std::string &path) {
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
    std::vector<int32_t> out_neighbors_i32(static_cast<size_t>(num_edges));
    read_vector(&file, &out_offsets, "out offsets");
    read_vector(&file, &out_neighbors_i32, "out neighbors");

    std::vector<int64_t> in_offsets;
    std::vector<int32_t> in_neighbors_i32;
    if (directed) {
        in_offsets.resize(static_cast<size_t>(num_nodes) + 1);
        in_neighbors_i32.resize(static_cast<size_t>(num_edges));
        read_vector(&file, &in_offsets, "in offsets");
        read_vector(&file, &in_neighbors_i32, "in neighbors");
    } else {
        in_offsets = out_offsets;
        in_neighbors_i32 = out_neighbors_i32;
    }

    Graph graph;
    graph.out_row_start.resize(static_cast<size_t>(num_nodes) + 1);
    graph.in_row_start.resize(static_cast<size_t>(num_nodes) + 1);
    graph.out_neighbors.resize(out_neighbors_i32.size());
    graph.in_neighbors.resize(in_neighbors_i32.size());
    graph.out_degree.resize(static_cast<size_t>(num_nodes));

    for (size_t v = 0; v <= static_cast<size_t>(num_nodes); ++v) {
        graph.out_row_start[v] = uint64_t(out_offsets[v]);
        graph.in_row_start[v] = uint64_t(in_offsets[v]);
    }
    for (size_t i = 0; i < graph.out_neighbors.size(); ++i) {
        graph.out_neighbors[i] = uint32_t(out_neighbors_i32[i]);
    }
    for (size_t i = 0; i < graph.in_neighbors.size(); ++i) {
        graph.in_neighbors[i] = uint32_t(in_neighbors_i32[i]);
    }
    for (size_t v = 0; v < static_cast<size_t>(num_nodes); ++v) {
        const uint64_t degree = graph.out_row_start[v + 1] - graph.out_row_start[v];
        graph.out_degree[v] = uint32_t(std::max<uint64_t>(degree, 1));
        std::sort(
            graph.out_neighbors.begin() + graph.out_row_start[v],
            graph.out_neighbors.begin() + graph.out_row_start[v + 1]);
        std::sort(
            graph.in_neighbors.begin() + graph.in_row_start[v],
            graph.in_neighbors.begin() + graph.in_row_start[v + 1]);
    }
    return graph;
}

inline double wall_seconds() {
#ifdef _OPENMP
    return omp_get_wtime();
#else
    return 0.0;
#endif
}

inline void enter_roi_if_needed(bool no_roi) {
    if (!no_roi) {
        const int status = std::system("gem5-bridge hypercall 4");
        if (status != 0) {
            std::cerr << "warning: ROI hypercall command exited with status "
                      << status << "\n";
        }
    }
}

inline void exit_roi_if_needed(bool no_roi) {
    if (!no_roi) {
        const int status = std::system("gem5-bridge hypercall 3");
        if (status != 0) {
            std::cerr << "warning: ROI end hypercall command exited with status "
                      << status << "\n";
        }
    }
}

inline void print_config(const char *kernel, const Options &opts) {
    std::cout << "STEP16_CONFIG kernel=" << kernel
              << " scale=" << opts.scale
              << " trials=" << opts.trials
              << " max_iters=" << opts.max_iters
              << " tolerance=" << opts.tolerance
              << " no_roi=" << (opts.no_roi ? 1 : 0)
#ifdef _OPENMP
              << " omp_threads=" << omp_get_max_threads()
#else
              << " omp_threads=1"
#endif
              << "\n";
}

inline void print_graph(const Graph &graph) {
    std::cout << "STEP16_GRAPH vertices=" << graph.out_degree.size()
              << " directed_edges=" << graph.out_neighbors.size()
              << " in_edges=" << graph.in_neighbors.size() << "\n";
}

inline uint32_t choose_source(size_t vertices, int trial) {
    return uint32_t(splitmix64(uint64_t(trial) + 0x1234ULL) % vertices);
}

#endif
