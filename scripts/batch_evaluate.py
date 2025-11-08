#!/usr/bin/env python3
"""
Batch evaluation over local PDFs in docs/dataset using the running API.
Generates:
- docs/eval_metrics.csv (per-document latency for Vanilla vs CG-RAG)
- docs/plots/latency_bar.png (average latency comparison)

Requires the API to be running at http://127.0.0.1:8000
Start it with: python -m uvicorn app.main:app --reload --port 8000
"""

import os
import time
import csv
from pathlib import Path
from typing import List, Tuple
import requests
import statistics
import matplotlib.pyplot as plt

API_BASE = "http://127.0.0.1:8000/api/v1"
RUN_EP = f"{API_BASE}/hackrx/run"

DATA_DIR = Path("docs/dataset")
OUT_CSV = Path("docs/eval_metrics.csv")
PLOT_DIR = Path("docs/plots")
PLOT_DIR.mkdir(parents=True, exist_ok=True)
PLOT_LAT = PLOT_DIR / "latency_bar.png"
PLOT_LEN = PLOT_DIR / "answer_length_bar.png"
PLOT_SUCC = PLOT_DIR / "success_rate_bar.png"

# A small, fixed question set suitable for policy PDFs
QUESTIONS: List[str] = [
    "What is the grace period for premium payment?",
    "Does this policy cover maternity expenses?",
    "What are the waiting periods for pre-existing diseases?",
]

HEADERS_BASE = {
    "Content-Type": "application/json",
    "Accept": "application/json",
}


def call_api(doc_path: str, use_graph: bool) -> Tuple[List[str], float, int]:
    payload = {"documents": doc_path, "questions": QUESTIONS}
    headers = dict(HEADERS_BASE)
    headers["X-Use-Graph"] = "true" if use_graph else "false"
    t0 = time.time()
    resp = requests.post(RUN_EP, json=payload, headers=headers, timeout=1200)
    elapsed = time.time() - t0
    if resp.status_code != 200:
        return [f"ERROR {resp.status_code}: {resp.text}"], elapsed, resp.status_code
    data = resp.json()
    return data.get("answers", []), elapsed, resp.status_code


def main() -> None:
    pdfs = sorted([p for p in DATA_DIR.glob("*.pdf") if p.is_file()])
    if not pdfs:
        print("No PDFs found in docs/dataset. Add files and rerun.")
        return

    rows = []
    print(f"Found {len(pdfs)} PDFs")
    for pdf in pdfs:
        print(f"\nEvaluating: {pdf}")

        ans_v, lat_v, code_v = call_api(str(pdf), use_graph=False)
        print(f"  Vanilla latency: {lat_v:.2f}s (HTTP {code_v})")

        ans_g, lat_g, code_g = call_api(str(pdf), use_graph=True)
        print(f"  CG-RAG latency: {lat_g:.2f}s (HTTP {code_g})")

        # Compute simple aggregates from answers
        def stats(ans: List[str]) -> Tuple[float, float]:
            if not ans:
                return 0.0, 0.0
            lengths = [len(a.strip()) for a in ans if isinstance(a, str)]
            nonempty = sum(1 for a in ans if isinstance(a, str) and a.strip())
            avg_len = sum(lengths) / len(lengths) if lengths else 0.0
            nonempty_rate = nonempty / max(1, len(ans))
            return avg_len, nonempty_rate

        v_len, v_rate = stats(ans_v)
        g_len, g_rate = stats(ans_g)

        rows.append([pdf.name, "Vanilla", f"{lat_v:.4f}", f"{v_len:.1f}", f"{v_rate:.2f}", code_v])
        rows.append([pdf.name, "CG-RAG", f"{lat_g:.4f}", f"{g_len:.1f}", f"{g_rate:.2f}", code_g])

    # Write CSV
    OUT_CSV.parent.mkdir(parents=True, exist_ok=True)
    with OUT_CSV.open("w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["document", "mode", "latency_s", "avg_answer_len", "nonempty_rate", "http_code"])
        for r in rows:
            w.writerow(r)
    print(f"Saved: {OUT_CSV}")

    # Aggregate and plot average latency by mode
    vanilla_lat = [float(r[2]) for r in rows if r[1] == "Vanilla"]
    graph_lat = [float(r[2]) for r in rows if r[1] == "CG-RAG"]

    avg_v = statistics.mean(vanilla_lat) if vanilla_lat else 0.0
    avg_g = statistics.mean(graph_lat) if graph_lat else 0.0

    plt.figure(figsize=(6,4))
    plt.bar(["Vanilla", "CG-RAG"], [avg_v, avg_g], color=["#8888ff", "#44cc88"])
    plt.ylabel("Average latency (s)")
    plt.title("Average Latency: Vanilla vs CG-RAG")
    for i, v in enumerate([avg_v, avg_g]):
        plt.text(i, v + 0.02, f"{v:.2f}s", ha="center")
    plt.tight_layout()
    plt.savefig(PLOT_LAT, dpi=150)
    print(f"Saved plot: {PLOT_LAT}")

    # Aggregate and plot average answer length
    vanilla_len = [float(r[3]) for r in rows if r[1] == "Vanilla"]
    graph_len = [float(r[3]) for r in rows if r[1] == "CG-RAG"]
    avg_len_v = statistics.mean(vanilla_len) if vanilla_len else 0.0
    avg_len_g = statistics.mean(graph_len) if graph_len else 0.0
    plt.figure(figsize=(6,4))
    plt.bar(["Vanilla", "CG-RAG"], [avg_len_v, avg_len_g], color=["#8888ff", "#44cc88"])
    plt.ylabel("Average answer length (chars)")
    plt.title("Answer Length: Vanilla vs CG-RAG")
    for i, v in enumerate([avg_len_v, avg_len_g]):
        plt.text(i, v + 1, f"{v:.0f}", ha="center")
    plt.tight_layout()
    plt.savefig(PLOT_LEN, dpi=150)
    print(f"Saved plot: {PLOT_LEN}")

    # Aggregate and plot non-empty answer rate
    vanilla_rate = [float(r[4]) for r in rows if r[1] == "Vanilla"]
    graph_rate = [float(r[4]) for r in rows if r[1] == "CG-RAG"]
    avg_rate_v = statistics.mean(vanilla_rate) if vanilla_rate else 0.0
    avg_rate_g = statistics.mean(graph_rate) if graph_rate else 0.0
    plt.figure(figsize=(6,4))
    plt.bar(["Vanilla", "CG-RAG"], [avg_rate_v, avg_rate_g], color=["#8888ff", "#44cc88"])
    plt.ylabel("Non-empty answer rate")
    plt.title("Success Rate: Vanilla vs CG-RAG")
    for i, v in enumerate([avg_rate_v, avg_rate_g]):
        plt.text(i, v + 0.01, f"{v:.2f}", ha="center")
    plt.ylim(0, 1)
    plt.tight_layout()
    plt.savefig(PLOT_SUCC, dpi=150)
    print(f"Saved plot: {PLOT_SUCC}")


if __name__ == "__main__":
    main()
