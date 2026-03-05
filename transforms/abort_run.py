#!/usr/bin/env python3
"""
Abort run (motif).

Use when the workflow decides it must stop and page/escalate. This transform:
- emits a structured JSON payload to stdout so the UI/run logs show *why*
- exits non-zero so the step fails and the run is marked failed

Inputs (optional):
- env ABORT_REASON: free-text
- env ABORT_SEVERITY: info|warning|critical (default critical)
"""

import json
import os
import sys
from datetime import datetime, timezone


def main() -> int:
    raw = sys.stdin.read()
    payload = json.loads(raw) if raw.strip() else {}
    step_id = ((payload or {}).get("step") or {}).get("step_id")
    run_id = (payload or {}).get("run_id")

    reason = (os.environ.get("ABORT_REASON") or "workflow aborted").strip()
    severity = (os.environ.get("ABORT_SEVERITY") or "critical").strip().lower() or "critical"

    now = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
    out_obj = {
        "status": "error",
        "error": {
            "type": "abort_run",
            "severity": severity,
            "reason": reason,
            "timestamp": now,
            "run_id": run_id,
            "step_id": step_id,
        },
    }
    json.dump(out_obj, sys.stdout)
    sys.stdout.write("\n")
    return 2


if __name__ == "__main__":
    raise SystemExit(main())

