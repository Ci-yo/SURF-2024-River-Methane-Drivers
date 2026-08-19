#!/usr/bin/env python3
import csv
import json
from pathlib import Path

root = Path(__file__).resolve().parents[1]
required = [
    "README.md", "DATA.md", "METHODOLOGY.md", "data/grime_curated.csv",
    "results/summary.json", "results/driver_correlations.csv", "assets/site-atlas.svg",
]
missing = [name for name in required if not (root / name).is_file()]
assert not missing, f"Missing required files: {missing}"

with (root / "data" / "grime_curated.csv").open(encoding="utf-8-sig", newline="") as handle:
    rows = list(csv.DictReader(handle))
assert len(rows) == 1113, f"Expected 1113 curated records, found {len(rows)}"
assert {"Site_ID", "Latitude", "Longitude", "Diffusive_CH4_Flux_Mean"}.issubset(rows[0])

summary = json.loads((root / "results" / "summary.json").read_text(encoding="utf-8"))
assert summary["records"] == len(rows)
print(f"Repository audit passed: {len(rows)} records, {summary['unique_sites']} sites")
