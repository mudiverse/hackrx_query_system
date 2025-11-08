#!/usr/bin/env python3
"""
Summarize evaluation results (docs/eval_results.md) into a layman-friendly report
using Gemini. Output: docs/eval_summary.md

Prereqs:
- Set GEMINI_API_KEY in .env or environment
- pip install -r requirements.txt

Usage:
  python scripts/summarize_eval.py
"""

import os
import sys
from pathlib import Path
from dotenv import load_dotenv
import google.generativeai as genai

from app.utils.config import Config


def main() -> None:
    load_dotenv()
    try:
        Config.validate()
    except Exception as e:
        print("Config validation warning:", e)
        # still try to proceed if GEMINI_API_KEY is available in env
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        print("GEMINI_API_KEY not set. Please add it to .env or environment.")
        sys.exit(1)

    genai.configure(api_key=api_key)
    model = genai.GenerativeModel(Config.GEMINI_GEN_MODEL)

    eval_path = Path("docs/eval_results.md")
    if not eval_path.exists():
        print("docs/eval_results.md not found. Run scripts/evaluate_rag.py first.")
        sys.exit(1)

    text = eval_path.read_text(encoding="utf-8")

    prompt = (
        "You are a helpful assistant. Read the evaluation results below and write a simple,"
        " layman-friendly summary that explains: (1) what was tested, (2) which approach was faster,"
        " (3) which approach is likely better for everyday users and why, and (4) a short conclusion."
        " Avoid jargon. Use short sentences and bullet points.\n\n"
        "Evaluation Results (Markdown):\n\n" + text
    )

    try:
        resp = model.generate_content(prompt)
        summary = (resp.text or "").strip()
    except Exception as e:
        print("Gemini API error:", e)
        sys.exit(1)

    out_path = Path("docs/eval_summary.md")
    out_path.write_text(summary, encoding="utf-8")
    print("Saved:", out_path)


if __name__ == "__main__":
    main()
