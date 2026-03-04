#!/usr/bin/env python3
"""
Transform: extract a stable items[] array from Zoho leads for foreach.

Input: context.fetch_leads.result (Zoho get_records payload).
Output:
- outputs/leads_raw.json (debug)
- stdout JSON includes items[] and lead_count so WIR can use:
  - items_path: "extract_items.items"
"""

import json
import os
import sys


def main() -> int:
    raw = sys.stdin.read()
    payload = json.loads(raw) if raw.strip() else {}
    ctx = (payload or {}).get("context") or {}

    fetch = (ctx or {}).get("fetch_leads") or {}
    result = (fetch or {}).get("result") or {}
    data = []
    if isinstance(result, dict):
        d = result.get("data")
        if isinstance(d, list):
            data = d
        elif isinstance(result.get("result"), dict):
            d = result["result"].get("data")
            if isinstance(d, list):
                data = d

    # Keep items reasonably small/stable: include id + a few common fields.
    items = []
    for lead in data:
        if not isinstance(lead, dict):
            continue
        items.append(
            {
                "id": lead.get("id"),
                "Full_Name": lead.get("Full_Name") or lead.get("Last_Name") or lead.get("Company"),
                "Email": lead.get("Email"),
                "Phone": lead.get("Phone"),
                "_raw": lead,  # keep full record for downstream transform convenience
            }
        )

    os.makedirs("outputs", exist_ok=True)
    out_path = "outputs/leads_raw.json"
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump({"count": len(items), "items": items}, f, ensure_ascii=False, indent=2)

    json.dump(
        {
            "status": "success",
            "files": [out_path],
            "outputs": [{"path": out_path, "title": "Zoho leads (raw)", "tags": ["zoho", "debug"]}],
            "lead_count": len(items),
            "items": items,
        },
        sys.stdout,
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
