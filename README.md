# workflow-test

Workflow repo for Deepalign complex workflow validation (Zoho → Transform → Postgres).

## Layout

```
workflow-test/
├── transforms/
│   ├── leads_to_md.py       # Zoho leads → markdown
│   ├── leads_extract_items.py  # Zoho leads → items[] for foreach
│   ├── lead_to_artifacts.py # foreach item → per-lead output files
│   ├── produce_context.py  # For motif: produces ready, branch, items
│   ├── echo_item.py        # For motif foreach
│   └── child_simple.py     # Minimal transform for child workflow / branches
└── README.md
```

## Transforms

| Script | Purpose |
|--------|---------|
| `leads_to_md.py` | Render Zoho leads into `outputs/leads.md` |
| `leads_extract_items.py` | Extract `items[]` from Zoho leads for foreach |
| `lead_to_artifacts.py` | Per-lead artifacts (inside foreach) |
| `produce_context.py` | Produce `ready`, `branch`, `items` for condition/switch/foreach |
| `echo_item.py` | Echo foreach item (motif validation) |
| `child_simple.py` | Minimal transform for child workflow / branches |

See [COMPLEX_WORKFLOW_VALIDATION.md](../../go/deepalign-enterprise-stack/docs/COMPLEX_WORKFLOW_VALIDATION.md) for full WIR payloads and verification.
