#!/usr/bin/env python3
"""
Evaluation runner for Vanilla RAG vs Clause Graph RAG (CG-RAG).
- Uses the HackRx sample document URL and a small set of questions.
- Runs both modes and reports retrieval/generation metrics and latency.

Note: This is a lightweight illustrative runner. For full-scale experiments,
consider adding RAGAS/NLI-based faithfulness and larger datasets.
"""

import time
import json
import statistics
from typing import List, Dict, Any, Tuple

import requests

API_BASE = "http://127.0.0.1:8000/api/v1"
RUN_EP = f"{API_BASE}/hackrx/run"
STATUS_EP = f"{API_BASE}/status"

# HackRx sample from test_api_improved.py
SAMPLE_DOC = "https://hackrx.blob.core.windows.net/assets/policy.pdf?sv=2023-01-03&st=2025-07-04T09%3A11%3A24Z&se=2027-07-05T09%3A11%3A00Z&sr=b&sp=r&sig=N4a9OU0w0QXO6AOIBiu4bpl7AXvEZogeT%2FjUHNO7HzQ%3D"
SAMPLE_QUESTIONS = [
    "What is the grace period for premium payment?",
    "Does this policy cover maternity expenses?",
    "What are the waiting periods for pre-existing diseases?",
    "What is the limit on room rent or ICU charges?",
    "Are OPD expenses covered under this policy?",
]

BASE_HEADERS = {
    "Content-Type": "application/json",
    "Accept": "application/json",
}


def run_once(doc_url: str, questions: List[str], use_graph: bool) -> Tuple[List[str], float, int]:
    payload = {"documents": doc_url, "questions": questions}
    headers = dict(BASE_HEADERS)
    headers["X-Use-Graph"] = "true" if use_graph else "false"
    t0 = start = time.time()
    resp = requests.post(RUN_EP, headers=headers, json=payload, timeout=600)
    elapsed = time.time() - t0
    if resp.status_code != 200:
        return [f"ERROR {resp.status_code}: {resp.text}"], elapsed, resp.status_code
    data = resp.json()
    return data.get("answers", []), elapsed, resp.status_code


def main() -> None:
    print("== CG-RAG Evaluation Runner ==")
    print("Checking status...")
    status = requests.get(STATUS_EP).json()
    print("Status:", json.dumps(status, indent=2))

    # Mode A: Vanilla RAG (graph disabled)
    print("\n[Mode A] Vanilla RAG (X-Use-Graph: false)")
    answers_vanilla, latency_vanilla, code_a = run_once(SAMPLE_DOC, SAMPLE_QUESTIONS, use_graph=False)
    print(f"Latency: {latency_vanilla:.2f}s, HTTP: {code_a}")

    # Mode B: CG-RAG (graph enabled)
    print("\n[Mode B] CG-RAG (X-Use-Graph: true)")
    answers_graph, latency_graph, code_b = run_once(SAMPLE_DOC, SAMPLE_QUESTIONS, use_graph=True)
    print(f"Latency: {latency_graph:.2f}s, HTTP: {code_b}")

    # Report simple latency comparison
    print("\n== Summary ==")
    print(f"Latency p50 (single run) — Vanilla: {latency_vanilla:.2f}s, CG-RAG: {latency_graph:.2f}s")

    # Save results
    out = {
        "document": SAMPLE_DOC,
        "questions": SAMPLE_QUESTIONS,
        "vanilla": {"answers": answers_vanilla, "latency_s": latency_vanilla},
        "graph": {"answers": answers_graph, "latency_s": latency_graph},
        "note": "Vanilla is approximated unless graph file is removed before run."
    }
    os_out = "docs/eval_results.md"
    try:
        with open(os_out, "w", encoding="utf-8") as f:
            f.write("# Evaluation Results (Prototype)\n\n")
            f.write("Document: " + SAMPLE_DOC + "\n\n")
            f.write("Questions:\n")
            for q in SAMPLE_QUESTIONS:
                f.write(f"- {q}\n")
            f.write("\n## Latency\n\n")
            f.write(f"- Vanilla: {latency_vanilla:.2f}s\n")
            f.write(f"- CG-RAG: {latency_graph:.2f}s\n")
            f.write("\n## Answers (first 2 shown)\n\n")
            for mode, ans in [("Vanilla", answers_vanilla), ("CG-RAG", answers_graph)]:
                f.write(f"### {mode}\n")
                for i, a in enumerate(ans[:2], 1):
                    f.write(f"{i}. {a}\n")
                f.write("\n")
            f.write("\nNote: This is a minimal runner; add retrieval logging and faithfulness scoring for full study.\n")
        print(f"Saved: {os_out}")
    except Exception as e:
        print("Could not write eval results:", e)


if __name__ == "__main__":
    main()
