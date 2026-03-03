#!/usr/bin/env python3
"""
Transform: echo foreach item (used inside foreach action).
Expects context.__foreach_item__ (or context.foreach_item from orchestrator).
Uses item value for filename when __foreach_index__ is absent.
"""

import json
import os
import sys


def main():
    raw = sys.stdin.read()
    payload = json.loads(raw) if raw.strip() else {}
    ctx = (payload or {}).get("context") or {}
    item = ctx.get("__foreach_item__") or ctx.get("foreach_item")
    idx = ctx.get("__foreach_index__", ctx.get("foreach_index", "?"))
    safe_name = str(item).replace("/", "_").replace("\\", "_")[:32] if item is not None else "none"

    os.makedirs("outputs", exist_ok=True)
    fn = f"outputs/echo_{safe_name}.txt"
    with open(fn, "w", encoding="utf-8") as f:
        f.write(f"item={json.dumps(item)}\nindex={idx}\n")

    json.dump({"status": "success", "files": [fn]}, sys.stdout)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
