#!/usr/bin/env python3
"""
Transform: inside foreach, write per-lead artifacts.

Expects:
- context.__foreach_item__ to be an object like:
  {"id": "...", "Full_Name": "...", "_raw": {...}}
"""

import json
import os
import re
import sys


def _safe(s: object) -> str:
    v = "" if s is None else str(s)
    v = re.sub(r"[^a-zA-Z0-9._-]+", "_", v)
    return v[:80] if v else "unknown"


def main() -> int:
    raw = sys.stdin.read()
    payload = json.loads(raw) if raw.strip() else {}
    ctx = (payload or {}).get("context") or {}
    item = ctx.get("__foreach_item__") or ctx.get("foreach_item") or {}

    if not isinstance(item, dict):
        item = {"value": item}

    lead_id = _safe(item.get("id"))
    lead_name = item.get("Full_Name") or item.get("Email") or lead_id
    raw_lead = item.get("_raw") if isinstance(item.get("_raw"), dict) else item

    os.makedirs("outputs/leads", exist_ok=True)
    json_path = f"outputs/leads/lead_{lead_id}.json"
    md_path = f"outputs/leads/lead_{lead_id}.md"

    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(raw_lead, f, ensure_ascii=False, indent=2)

    with open(md_path, "w", encoding="utf-8") as f:
        f.write("# Lead\n\n")
        f.write(f"- id: `{lead_id}`\n")
        f.write(f"- name: `{lead_name}`\n")

    json.dump(
        {
            "status": "success",
            "files": [json_path, md_path],
            "outputs": [
                {"path": json_path, "title": f"Lead {lead_id} (json)", "tags": ["zoho", "lead"]},
                {"path": md_path, "title": f"Lead {lead_id} (md)", "mime_type": "text/markdown", "tags": ["zoho", "lead"]},
            ],
            "lead_id": lead_id,
        },
        sys.stdout,
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
