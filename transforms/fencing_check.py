#!/usr/bin/env python3
"""
Fencing check (motif).

Real fencing is environment-specific (Kubernetes/Patroni, cloud instance stop, VIP move, STONITH, etc.).
This transform emits a simple signal `can_fence` so ai_decide can reason about split-brain risk.

Inputs (optional):
- env FENCING_OK: "true" | "false" (default false)
- env FENCING_METHOD: free-text (e.g. "patroni", "cloud-stop", "iptables", "manual")

Output:
- writes outputs/fencing_status.json
- returns can_fence + method + reason
"""

import json
import os
import sys
from datetime import datetime, timezone


def _bool_env(name: str, default: bool = False) -> bool:
    v = (os.environ.get(name) or "").strip().lower()
    if v in ("1", "true", "yes", "y", "on"):
        return True
    if v in ("0", "false", "no", "n", "off"):
        return False
    return default


def main() -> int:
    _raw = sys.stdin.read()  # payload unused for now; keep contract stable

    now = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
    can_fence = _bool_env("FENCING_OK", default=False)
    method = (os.environ.get("FENCING_METHOD") or "unknown").strip() or "unknown"

    reason = "ok" if can_fence else "fencing_not_confirmed"
    out_obj = {
        "checked_at": now,
        "can_fence": can_fence,
        "method": method,
        "reason": reason,
    }

    os.makedirs("outputs", exist_ok=True)
    out_path = "outputs/fencing_status.json"
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(out_obj, f, indent=2, sort_keys=True)

    json.dump(
        {
            "status": "success",
            "files": [out_path],
            "outputs": [{"path": out_path, "title": "Fencing status", "tags": ["dr", "safety"]}],
            **out_obj,
        },
        sys.stdout,
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

