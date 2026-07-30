"""Export : ecriture du resultat dans un format ouvert."""
from __future__ import annotations

import csv
import json
from pathlib import Path

from .models import ProtectedArea


def export_json(records: list[ProtectedArea], path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as fh:
        json.dump([record.to_dict() for record in records], fh, ensure_ascii=False, indent=2)


def export_csv(records: list[ProtectedArea], path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if not records:
        path.write_text("", encoding="utf-8")
        return
    fieldnames = list(records[0].to_dict().keys())
    with path.open("w", encoding="utf-8", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=fieldnames)
        writer.writeheader()
        for record in records:
            writer.writerow(record.to_dict())
