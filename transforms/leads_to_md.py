#!/usr/bin/env python3
"""
Transform: render Zoho leads (context.fetch_leads) into outputs/leads.md.
Contract: prints JSON stdout with files under outputs/.
"""

import json
import os
import sys
from datetime import datetime


def _safe_str(x):
    try:
        return "" if x is None else str(x)
    except Exception:
        return ""


def main():
    raw = sys.stdin.read()
    if not raw.strip():
        print("transform input missing (expected JSON on stdin)", file=sys.stderr)
        return 1
    try:
        payload = json.loads(raw)
    except Exception as e:
        print(f"failed to parse transform stdin JSON: {e}", file=sys.stderr)
        return 1

    context = (payload or {}).get("context") or {}
    fetch = (context or {}).get("fetch_leads") or {}
    result = fetch.get("result") or {}
    rows = []
    # Zoho can return {"data":[...]} or nested {"result":{"data":[...]}}
    if isinstance(result, dict):
        data = result.get("data")
        if not isinstance(data, list) and isinstance(result.get("result"), dict):
            data = result["result"].get("data")
        if isinstance(data, list):
            rows = data

    os.makedirs("outputs", exist_ok=True)
    out_path = os.path.join("outputs", "leads.md")

    now = datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")
    with open(out_path, "w", encoding="utf-8") as f:
        f.write(f"# Zoho Leads Report\n\n")
        f.write(f"- Generated: `{now}`\n")
        f.write(f"- Lead count: **{len(rows)}**\n\n")
        for i, lead in enumerate(rows[:50], start=1):
            if not isinstance(lead, dict):
                continue
            name = _safe_str(lead.get("Full_Name") or lead.get("Last_Name") or lead.get("Company") or lead.get("id") or f"lead-{i}")
            email = _safe_str(lead.get("Email") or "")
            phone = _safe_str(lead.get("Phone") or "")
            lid = _safe_str(lead.get("id") or "")
            f.write(f"## {i}. {name}\n\n")
            if lid:
                f.write(f"- id: `{lid}`\n")
            if email:
                f.write(f"- email: `{email}`\n")
            if phone:
                f.write(f"- phone: `{phone}`\n")
            try:
                snippet = json.dumps({k: lead.get(k) for k in list(lead.keys())[:10]}, ensure_ascii=False)
            except Exception:
                snippet = ""
            if snippet:
                f.write(f"\n```json\n{snippet}\n```\n\n")

    json.dump({"status": "success", "files": ["outputs/leads.md"]}, sys.stdout)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
