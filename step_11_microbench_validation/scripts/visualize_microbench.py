#!/usr/bin/env python3
# Copyright (c) 2026
# SPDX-License-Identifier: BSD-3-Clause

"""Parse Step 11 MB_RESULT lines and draw a compact SVG comparison."""

import argparse
import csv
import html
import math
import re
from pathlib import Path


RESULT_RE = re.compile(r"\bMB_RESULT\s+(.*)$")


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
        "bench",
        "mib",
        "passes",
        "stride",
        "seconds",
        "ops",
        "ns_per_op",
        "bandwidth_mib_s",
        "checksum",
        "source",
    ]
    with path.open("w", newline="") as out:
        writer = csv.DictWriter(out, fieldnames=columns, extrasaction="ignore")
        writer.writeheader()
        for row in rows:
            writer.writerow(row)


def svg_bar_chart(rows: list[dict[str, str]]) -> str:
    benches = sorted({row.get("bench", "") for row in rows})
    runs = sorted({row.get("run", "") for row in rows})
    groups = [(run, bench) for run in runs for bench in benches]
    width = max(900, 110 + 92 * len(groups))
    panel_h = 260
    height = 640
    left = 70
    right = 30
    top_a = 52
    top_b = 360
    plot_w = width - left - right
    colors = {"0": "#277da1", "1": "#f94144"}

    def row_for(run: str, bench: str, node: str) -> dict[str, str] | None:
        matches = [
            row for row in rows
            if row.get("run") == run and row.get("bench") == bench and
            row.get("node") == node
        ]
        return matches[-1] if matches else None

    max_latency = max(number(row, "ns_per_op") for row in rows) or 1.0
    max_bw = max(number(row, "bandwidth_mib_s") for row in rows) or 1.0
    group_w = plot_w / max(1, len(groups))
    bar_w = min(24, group_w * 0.32)

    svg: list[str] = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">',
        "<style>",
        "text{font-family:Arial,Helvetica,sans-serif;font-size:12px;fill:#202124}",
        ".title{font-size:18px;font-weight:700}.axis{stroke:#333;stroke-width:1}",
        ".grid{stroke:#d8d8d8;stroke-width:1}.label{font-size:11px}.note{fill:#555}",
        "</style>",
        '<rect width="100%" height="100%" fill="#fff"/>',
        f'<text x="{left}" y="28" class="title">Step 11 NUMA Microbenchmark Results</text>',
    ]

    def panel(title: str, top: int, metric: str, max_value: float,
              higher_is_better: bool) -> None:
        svg.append(f'<text x="{left}" y="{top - 18}" class="title">{html.escape(title)}</text>')
        for frac in (0.25, 0.5, 0.75, 1.0):
            y = top + panel_h - frac * panel_h
            value = max_value * frac
            svg.append(f'<line x1="{left}" y1="{y:.1f}" x2="{width - right}" y2="{y:.1f}" class="grid"/>')
            svg.append(f'<text x="8" y="{y + 4:.1f}" class="label">{value:.1f}</text>')
        svg.append(f'<line x1="{left}" y1="{top + panel_h}" x2="{width - right}" y2="{top + panel_h}" class="axis"/>')
        svg.append(f'<line x1="{left}" y1="{top}" x2="{left}" y2="{top + panel_h}" class="axis"/>')
        for idx, (run, bench) in enumerate(groups):
            center = left + idx * group_w + group_w / 2
            for node, delta in (("0", -bar_w / 1.8), ("1", bar_w / 1.8)):
                row = row_for(run, bench, node)
                if row is None:
                    continue
                value = number(row, metric)
                bar_h = value / max_value * panel_h
                x = center + delta - bar_w / 2
                y = top + panel_h - bar_h
                svg.append(
                    f'<rect x="{x:.1f}" y="{y:.1f}" width="{bar_w:.1f}" height="{bar_h:.1f}" '
                    f'fill="{colors[node]}"><title>{html.escape(run)} {html.escape(bench)} '
                    f'node {node}: {value:.3f}</title></rect>'
                )
            label = html.escape(bench.replace("_", " "))
            svg.append(
                f'<text transform="translate({center - 22:.1f},{top + panel_h + 72}) rotate(-45)" '
                f'class="label">{label}</text>'
            )
        note = "higher is better" if higher_is_better else "lower is better"
        svg.append(f'<text x="{width - right - 120}" y="{top - 18}" class="note">{note}</text>')

    panel("Access Time (ns/op)", top_a, "ns_per_op", max_latency, False)
    panel("Touched Bandwidth (MiB/s)", top_b, "bandwidth_mib_s", max_bw, True)
    svg.extend([
        f'<rect x="{left}" y="{height - 34}" width="12" height="12" fill="{colors["0"]}"/>',
        f'<text x="{left + 18}" y="{height - 24}">node 0</text>',
        f'<rect x="{left + 86}" y="{height - 34}" width="12" height="12" fill="{colors["1"]}"/>',
        f'<text x="{left + 104}" y="{height - 24}">node 1</text>',
        "</svg>",
    ])
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
        raise SystemExit("no MB_RESULT lines found in the provided outdir(s)")

    csv_path = args.csv or (args.outdirs[0] / "microbench_results.csv")
    svg_path = args.svg or (args.outdirs[0] / "microbench_results.svg")
    write_csv(csv_path, rows)
    svg_path.write_text(svg_bar_chart(rows))

    print(f"parsed {len(rows)} benchmark rows")
    print(f"wrote {csv_path}")
    print(f"wrote {svg_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
