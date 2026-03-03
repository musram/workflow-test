#!/usr/bin/env python3
"""
Transform: produce context for condition/switch/foreach.
Outputs: outputs/context.json AND puts ready, branch, items in stdout result
so condition/switch/foreach can read them via produce.ready, produce.branch, produce.items.
"""

import json
import os
import sys


def main():
    raw = sys.stdin.read()
    payload = json.loads(raw) if raw.strip() else {}
    context = (payload or {}).get("context") or {}

    # Produce deterministic values for routing (must be in stdout for context propagation)
    out_data = {"ready": True, "branch": "case_a", "items": [1, 2, 3]}

    os.makedirs("outputs", exist_ok=True)
    out_path = "outputs/context.json"
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(out_data, f, indent=2)

    result = {
        "status": "success",
        "files": [out_path],
        "outputs": [{"path": out_path, "title": "Context", "tags": ["motif"]}],
        "ready": out_data["ready"],
        "branch": out_data["branch"],
        "items": out_data["items"],
    }
    json.dump(result, sys.stdout)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
