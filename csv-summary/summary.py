"""Summarise deployment outcomes from a mounted CSV file."""

import argparse
import csv
import json
from collections import Counter
from pathlib import Path

REQUIRED = {"service", "environment", "outcome"}


def summarise(source: Path) -> dict:
    with source.open(newline="", encoding="utf-8") as stream:
        reader = csv.DictReader(stream)
        if not REQUIRED.issubset(reader.fieldnames or []):
            raise ValueError(f"CSV must contain: {', '.join(sorted(REQUIRED))}")
        rows = list(reader)
    if any(not all(row[field].strip() for field in REQUIRED) for row in rows):
        raise ValueError("CSV contains a blank required value")
    return {
        "total_deployments": len(rows),
        "by_outcome": dict(sorted(Counter(row["outcome"].strip().lower() for row in rows).items())),
        "by_environment": dict(sorted(Counter(row["environment"].strip().lower() for row in rows).items())),
        "unique_services": sorted({row["service"].strip() for row in rows}),
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=Path, required=True, help="Mounted CSV input")
    parser.add_argument("--output", type=Path, required=True, help="Mounted JSON output")
    args = parser.parse_args()
    result = summarise(args.input)
    args.output.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(f"Processed {result['total_deployments']} deployments; wrote {args.output}")


if __name__ == "__main__":
    main()
