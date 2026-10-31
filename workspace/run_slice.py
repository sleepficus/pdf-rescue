#!/usr/bin/env python3
from pathlib import Path
import json
from pdfslice.pipeline import run

if __name__ == "__main__":
    root = Path(__file__).resolve().parents[1]
    result = run(root, "/Users/carrie/.cache/codex-runtimes/codex-primary-runtime/dependencies/bin/override/pdftoppm")
    print(json.dumps({"all_expected": result["all_expected"], "all_deterministic": result["all_deterministic"], "sources_unchanged": result["all_sources_unchanged"]}, sort_keys=True))
