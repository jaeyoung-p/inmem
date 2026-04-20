#!/usr/bin/env python3
# Copyright (c) 2026
# SPDX-License-Identifier: BSD-3-Clause

"""Parse BWL_RESULT lines and draw a bandwidth-vs-loaded-latency SVG."""

import argparse
import csv
import html
import math
import re
from pathlib import Path


RESULT_RE = re.compile(r"\bBWL_RESULT\s+(.*)$")


def parse_tokens(text: str) -> dict[str, str]:
    fields: dict[str, str] = {}
    for token in text.split():
        if "=" not in token:
            continue
        key, value = token.split("=", 1)
        fields[key] = value
    return fields


def result_files(outdir: Path) -> list[Path]:
    candidates = []
    for pattern in ("*.device", "simout", "*.log", "*.txt"):
        candidates.extend(outdir.glob(pattern))
    return sorted({path for path in candidates if path.is_file()})


def parse_outdir(outdir: Path) -> list[dict[str, str]]:
    rows: list[dict[str, str]] = []
    for path in result_files(outdir):
        for line in path.read_text(errors="replace").splitlines():
            match = RESULT_RE.search(line)
            if not match:
                continue
            row = parse_tokens(match.group(1))
            row["run"] = outdir.name
            row["source"] = str(path)
            rows.append(row)
    return rows


def number(row: dict[str, str], key: str) -> float:
    try:
        value = float(row[key])
    except (KeyError, ValueError):
        return 0.0
    return value if math.isfinite(value) else 0.0


def write_csv(path: Path, rows: list[dict[str, str]]) -> None:
    columns = [
        "run",
        "node",
        "workers",
        "worker_mib",
        "latency_mib",
        "latency_iters",
        "cpu_mhz",
        "cycles",
        "seconds",
        "clock_seconds",
        "worker_bytes",
        "bandwidth_mib_s",
        "latency_ns",
        "checksum",
        "source",
    ]
    with path.open("w", newline="") as out:
        writer = csv.DictWriter(out, fieldnames=columns, extrasaction="ignore")
        writer.writeheader()
        for row in rows:
            writer.writerow(row)


def nice_tick(value: float) -> str:
    if value >= 1000.0:
        return f"{value:.0f}"
    if value >= 100.0:
        return f"{value:.1f}"
    return f"{value:.2f}"


def svg_chart(rows: list[dict[str, str]]) -> str:
    width = 960
    height = 620
    left = 88
    right = 44
    top = 58
    bottom = 92
    plot_w = width - left - right
    plot_h = height - top - bottom
    colors = {"0": "#1f77b4", "1": "#d62728"}

    nodes = sorted({row.get("node", "") for row in rows})
    max_bw = max(number(row, "bandwidth_mib_s") for row in rows) or 1.0
    max_lat = max(number(row, "latency_ns") for row in rows) or 1.0
    max_bw *= 1.08
    max_lat *= 1.08

    def x_for(value: float) -> float:
        return left + (value / max_bw) * plot_w

    def y_for(value: float) -> float:
        return top + plot_h - (value / max_lat) * plot_h

    svg: list[str] = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">',
        "<style>",
        "text{font-family:Arial,Helvetica,sans-serif;font-size:12px;fill:#202124}",
        ".title{font-size:19px;font-weight:700}.axis{stroke:#333;stroke-width:1}",
        ".grid{stroke:#dddddd;stroke-width:1}.label{font-size:12px}.note{fill:#555}",
        ".series{fill:none;stroke-width:2}.point{stroke:#fff;stroke-width:1}",
        "</style>",
        '<rect width="100%" height="100%" fill="#fff"/>',
        f'<text x="{left}" y="30" class="title">NUMA Bandwidth vs Loaded Latency</text>',
        f'<line x1="{left}" y1="{top + plot_h}" x2="{left + plot_w}" y2="{top + plot_h}" class="axis"/>',
        f'<line x1="{left}" y1="{top}" x2="{left}" y2="{top + plot_h}" class="axis"/>',
    ]

    for tick in range(0, 6):
        frac = tick / 5.0
        x = left + frac * plot_w
        bw = frac * max_bw
        svg.append(f'<line x1="{x:.1f}" y1="{top}" x2="{x:.1f}" y2="{top + plot_h}" class="grid"/>')
        svg.append(f'<text x="{x - 16:.1f}" y="{top + plot_h + 24}" class="label">{nice_tick(bw)}</text>')

        y = top + plot_h - frac * plot_h
        lat = frac * max_lat
        svg.append(f'<line x1="{left}" y1="{y:.1f}" x2="{left + plot_w}" y2="{y:.1f}" class="grid"/>')
        svg.append(f'<text x="18" y="{y + 4:.1f}" class="label">{nice_tick(lat)}</text>')

    svg.append(f'<text x="{left + plot_w / 2 - 70:.1f}" y="{height - 30}" class="label">Injected read bandwidth (MiB/s)</text>')
    svg.append(f'<text transform="translate(22,{top + plot_h / 2 + 72:.1f}) rotate(-90)" class="label">Pointer-chase loaded latency (ns)</text>')

    for node in nodes:
        node_rows = sorted(
            [row for row in rows if row.get("node") == node],
            key=lambda row: (number(row, "bandwidth_mib_s"), number(row, "workers")),
        )
        if not node_rows:
            continue
        color = colors.get(node, "#555555")
        points = [
            f'{x_for(number(row, "bandwidth_mib_s")):.1f},'
            f'{y_for(number(row, "latency_ns")):.1f}'
            for row in node_rows
        ]
        svg.append(
            f'<polyline class="series" stroke="{color}" points="{" ".join(points)}"/>'
        )
        for row in node_rows:
            x = x_for(number(row, "bandwidth_mib_s"))
            y = y_for(number(row, "latency_ns"))
            workers = html.escape(row.get("workers", "?"))
            bw = number(row, "bandwidth_mib_s")
            lat = number(row, "latency_ns")
            svg.append(
                f'<circle class="point" cx="{x:.1f}" cy="{y:.1f}" r="4.5" fill="{color}">'
                f'<title>node {html.escape(node)}, workers {workers}: {bw:.3f} MiB/s, {lat:.3f} ns</title>'
                "</circle>"
            )

    legend_x = left
    legend_y = height - 58
    for idx, node in enumerate(nodes):
        color = colors.get(node, "#555555")
        x = legend_x + idx * 104
        svg.append(f'<rect x="{x}" y="{legend_y}" width="14" height="14" fill="{color}"/>')
        svg.append(f'<text x="{x + 20}" y="{legend_y + 12}">node {html.escape(node)}</text>')

    svg.append('<text x="620" y="30" class="note">higher/right is more bandwidth; higher/up is more latency</text>')
    svg.append("</svg>")
    return "\n".join(svg)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("outdirs", nargs="+", type=Path)
    parser.add_argument("--csv", type=Path, default=None)
    parser.add_argument("--svg", type=Path, default=None)
    args = parser.parse_args()

    rows: list[dict[str, str]] = []
    for outdir in args.outdirs:
        rows.extend(parse_outdir(outdir))
    if not rows:
        raise SystemExit("no BWL_RESULT lines found in the provided outdir(s)")

    csv_path = args.csv or (args.outdirs[0] / "bw_latency_results.csv")
    svg_path = args.svg or (args.outdirs[0] / "bw_latency_results.svg")
    write_csv(csv_path, rows)
    svg_path.write_text(svg_chart(rows))

    print(f"parsed {len(rows)} bandwidth/latency rows")
    print(f"wrote {csv_path}")
    print(f"wrote {svg_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
