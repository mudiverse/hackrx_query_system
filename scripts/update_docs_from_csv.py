#!/usr/bin/env python3
"""
Read docs/eval_metrics.csv, compute simple aggregates, and write a markdown summary to docs/metrics_summary.md.
This avoids risky in-place edits of the main paper; you can paste the generated table into docs/paper_draft.md and docs/rag_comparative.md.

Metrics computed:
- Average latency per mode (Vanilla, CG-RAG)
- Count of evaluated PDFs
"""

import csv
from pathlib import Path
import statistics

CSV_PATH = Path("docs/eval_metrics.csv")
OUT_PATH = Path("docs/metrics_summary.md")


def main() -> None:
    if not CSV_PATH.exists():
        print("CSV not found:", CSV_PATH)
        return

    rows = []
    with CSV_PATH.open("r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for r in reader:
            rows.append(r)

    docs = sorted(set(r["document"] for r in rows))

    lat_v = [float(r["latency_s"]) for r in rows if r["mode"] == "Vanilla"]
    lat_g = [float(r["latency_s"]) for r in rows if r["mode"] == "CG-RAG"]

    avg_v = statistics.mean(lat_v) if lat_v else 0.0
    avg_g = statistics.mean(lat_g) if lat_g else 0.0

    md = []
    md.append("# Metrics Summary (from eval_metrics.csv)\n")
    md.append(f"Documents evaluated: {len(docs)}\n")
    md.append("\n| Metric | Vanilla RAG | CG-RAG |\n|---|---:|---:|\n")
    md.append(f"| Avg Latency (s) | {avg_v:.2f} | {avg_g:.2f} |\n")
    md.append("\nSee plot: docs/plots/latency_bar.png\n")

    OUT_PATH.write_text("\n".join(md), encoding="utf-8")
    print("Wrote:", OUT_PATH)


if __name__ == "__main__":
    main()
