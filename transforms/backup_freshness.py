#!/usr/bin/env python3
"""
Backup freshness (motif).

This is intentionally provider-agnostic. In real deployments you would query:
- backup system metadata (e.g., pgBackRest, WAL-G, cloud snapshots)
- WAL archiving health

Inputs (optional):
- env BACKUP_LAST_SUCCESS_RFC3339: e.g. "2026-03-05T12:00:00Z"
- env BACKUP_LAST_SUCCESS_EPOCH: seconds since epoch
- env BACKUP_MAX_AGE_SECONDS: default 3600 (1h)

Output:
- writes outputs/backup_freshness.json
- returns fields used by ai_decide: last_success_at, age_seconds, max_age_seconds, fresh
"""

import json
import os
import sys
from datetime import datetime, timezone


def _now_utc() -> datetime:
    return datetime.now(timezone.utc)


def _parse_rfc3339(s: str) -> datetime | None:
    s = (s or "").strip()
    if not s:
        return None
    # Accept trailing Z.
    if s.endswith("Z"):
        s = s[:-1] + "+00:00"
    try:
        return datetime.fromisoformat(s)
    except Exception:
        return None


def main() -> int:
    raw = sys.stdin.read()
    payload = json.loads(raw) if raw.strip() else {}
    _context = (payload or {}).get("context") or {}

    max_age_seconds = int(os.environ.get("BACKUP_MAX_AGE_SECONDS") or "3600")
    if max_age_seconds < 60:
        max_age_seconds = 60

    last_success_at: datetime | None = None
    rfc = os.environ.get("BACKUP_LAST_SUCCESS_RFC3339") or ""
    last_success_at = _parse_rfc3339(rfc)

    if last_success_at is None:
        ep = (os.environ.get("BACKUP_LAST_SUCCESS_EPOCH") or "").strip()
        if ep:
            try:
                last_success_at = datetime.fromtimestamp(int(ep), tz=timezone.utc)
            except Exception:
                last_success_at = None

    now = _now_utc()
    if last_success_at is None:
        age_seconds = None
        fresh = False
        reason = "missing BACKUP_LAST_SUCCESS_RFC3339/BACKUP_LAST_SUCCESS_EPOCH"
    else:
        age_seconds = int((now - last_success_at).total_seconds())
        fresh = age_seconds <= max_age_seconds
        reason = "ok" if fresh else "stale"

    out_obj = {
        "checked_at": now.isoformat().replace("+00:00", "Z"),
        "last_success_at": (last_success_at.isoformat().replace("+00:00", "Z") if last_success_at else None),
        "age_seconds": age_seconds,
        "max_age_seconds": max_age_seconds,
        "fresh": fresh,
        "reason": reason,
    }

    os.makedirs("outputs", exist_ok=True)
    out_path = "outputs/backup_freshness.json"
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(out_obj, f, indent=2, sort_keys=True)

    json.dump(
        {
            "status": "success",
            "files": [out_path],
            "outputs": [{"path": out_path, "title": "Backup freshness", "tags": ["dr", "backup"]}],
            **out_obj,
        },
        sys.stdout,
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

