#!/usr/bin/env python3
"""Inventory a KiCAD project directory.

Datasheets are expected to be linked from component fields. Local datasheet
files are reported only as optional fallback material.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


DATASHEET_EXTENSIONS = {
    ".pdf",
    ".txt",
    ".md",
    ".html",
    ".htm",
}


IGNORED_DIR_NAMES = {
    ".git",
    ".history",
    "datasheet_cache",
    "review_outputs",
    "__pycache__",
}


REVIEW_ARTIFACT_NAMES = {
    "schematic_review.md",
    "review.md",
    "hardware_review.md",
}


def find_project_root(path: Path) -> Path:
    path = path.resolve()
    if path.is_file():
        if path.suffix in {".kicad_pro", ".kicad_sch", ".kicad_pcb"}:
            return path.parent
        return path.parent
    return path


def is_local_datasheet_candidate(path: Path) -> bool:
    """Avoid reporting review/checklist markdown as datasheet fallback material."""
    if path.suffix.lower() not in DATASHEET_EXTENSIONS:
        return False
    name = path.name.lower()
    if name in REVIEW_ARTIFACT_NAMES:
        return False
    if "checklist" in name or "review" in name:
        return False
    return True


def normalized_tokens(text: str) -> set[str]:
    separators = "-_.,()[]{}+ "
    cleaned = text.lower()
    for sep in separators:
        cleaned = cleaned.replace(sep, " ")
    return {token for token in cleaned.split() if len(token) >= 2}


def component_match_score(component: dict[str, Any], datasheet: Path) -> int:
    filename_tokens = normalized_tokens(datasheet.stem)
    fields = [
        component.get("reference", ""),
        component.get("value", ""),
        component.get("lib_id", ""),
        component.get("description", ""),
        component.get("datasheet", ""),
    ]
    score = 0
    for field in fields:
        field_tokens = normalized_tokens(str(field))
        overlap = filename_tokens & field_tokens
        score += len(overlap)
        compact_field = str(field).lower().replace(":", "_").replace("/", "_")
        if compact_field and compact_field in datasheet.stem.lower():
            score += 3
    return score


def discover(root: Path) -> dict[str, Any]:
    project_root = find_project_root(root)
    files = [
        path
        for path in project_root.rglob("*")
        if not any(part in IGNORED_DIR_NAMES or part.startswith(".") for part in path.parts)
    ]

    schematic_files = sorted(str(p) for p in files if p.suffix == ".kicad_sch")
    project_files = sorted(str(p) for p in files if p.suffix == ".kicad_pro")
    pcb_files = sorted(str(p) for p in files if p.suffix == ".kicad_pcb")
    local_datasheets = sorted(
        str(p)
        for p in files
        if p.is_file() and is_local_datasheet_candidate(p)
    )

    return {
        "project_root": str(project_root),
        "project_files": project_files,
        "schematic_files": schematic_files,
        "pcb_files": pcb_files,
        "local_datasheets": local_datasheets,
        "suggested_output_dirs": {
            "datasheet_cache": str(project_root / "datasheet_cache"),
            "review_outputs": str(project_root / "review_outputs"),
        },
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Inventory a KiCAD project")
    parser.add_argument("path", type=Path, help="Project directory or KiCAD file")
    parser.add_argument("--pretty", action="store_true", help="Pretty-print JSON")
    args = parser.parse_args()

    inventory = discover(args.path)
    indent = 2 if args.pretty else None
    print(json.dumps(inventory, ensure_ascii=False, indent=indent))


if __name__ == "__main__":
    main()
