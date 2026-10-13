from __future__ import annotations

import csv
import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parent
ARCHIVE = ROOT / "archives" / "shanghai_house_dataset_v2_v3.zip"
DATASET = ROOT / "extracted" / "shanghai_house_dataset"


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as source:
        for chunk in iter(lambda: source.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest().upper()


def inspect_csv(path: Path) -> dict[str, object]:
    with path.open("r", encoding="utf-8-sig", newline="") as source:
        reader = csv.reader(source)
        header = next(reader)
        rows = 0
        malformed_rows = 0
        min_columns = len(header)
        max_columns = len(header)
        for row in reader:
            rows += 1
            width = len(row)
            min_columns = min(min_columns, width)
            max_columns = max(max_columns, width)
            if width != len(header):
                malformed_rows += 1

    return {
        "path": path.relative_to(DATASET).as_posix(),
        "bytes": path.stat().st_size,
        "sha256": sha256(path),
        "data_rows": rows,
        "columns": len(header),
        "min_columns": min_columns,
        "max_columns": max_columns,
        "malformed_rows": malformed_rows,
        "header": header,
    }


report = {
    "archive": {
        "path": ARCHIVE.relative_to(ROOT).as_posix(),
        "bytes": ARCHIVE.stat().st_size,
        "sha256": sha256(ARCHIVE),
    },
    "csv_files": [inspect_csv(path) for path in sorted(DATASET.rglob("*.csv"))],
}

print(json.dumps(report, ensure_ascii=False, indent=2))
