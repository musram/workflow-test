#!/usr/bin/env python3
"""
Minimal transform: writes outputs/child_out.txt.
Used by child workflow and motif branch steps.
"""

import os
import sys
import json

os.makedirs("outputs", exist_ok=True)
with open("outputs/child_out.txt", "w", encoding="utf-8") as f:
    f.write("child_workflow_completed\n")
json.dump({"status": "success", "files": ["outputs/child_out.txt"]}, sys.stdout)
