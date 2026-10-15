"""Tiny demo job for the Kubernetes CronJob lab.

Each run it:
  1. reads a greeting from the environment (comes from a ConfigMap),
  2. checks that an API token is set (comes from a Secret) without printing it,
  3. appends a timestamp to a file on the state volume and reports how many runs it has seen.

It exists only to show how configuration, secrets and persistent state reach a
CronJob. It does not call any external service.
"""
import os
import sys
from datetime import datetime, timezone
from pathlib import Path

greeting = os.getenv("GREETING", "(GREETING not set)")
token = os.getenv("API_TOKEN")
state_dir = Path(os.getenv("STATE_DIR", "./state"))

print(f"Greeting: {greeting}")
if token:
    print(f"API_TOKEN is set ({len(token)} characters; value not printed)")
else:
    print("API_TOKEN is NOT set")

try:
    state_dir.mkdir(parents=True, exist_ok=True)
    runs_file = state_dir / "runs.txt"
    with open(runs_file, "a", encoding="utf-8") as f:
        f.write(datetime.now(timezone.utc).isoformat() + "\n")
    count = sum(1 for _ in open(runs_file, encoding="utf-8"))
except OSError as e:
    print(f"Could not write state in {state_dir}: {e}", file=sys.stderr)
    sys.exit(1)

print(f"This is run number {count} (state file: {runs_file})")
