#!/usr/bin/env python3
"""Build a compact review context for a KiCAD project."""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path
from typing import Any

SCRIPT_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(SCRIPT_DIR))

from extract_kicad_sch import extract  # noqa: E402
from inventory_project import discover  # noqa: E402


def cache_stem(value: str, datasheet: str) -> str:
    part = "".join(ch if ch.isalnum() or ch in "._-" else "_" for ch in value.strip()) or "part"
    digest = hashlib.sha1(datasheet.encode("utf-8")).hexdigest()[:8] if datasheet else "no_ds"
    return f"{part}_{digest}"


def is_ic_candidate(component: dict[str, Any]) -> bool:
    reference = component.get("reference", "")
    lib_id = component.get("lib_id", "").lower()
    datasheet = component.get("datasheet", "")
    pin_count = len(component.get("pins", []))

    if reference.startswith("U"):
        return True
    if any(token in lib_id for token in ["driver", "mcu", "processor", "regulator", "converter"]):
        return True
    return bool(datasheet and pin_count >= 6 and not reference.startswith(("J", "P", "TP")))


def is_current_critical_candidate(component: dict[str, Any]) -> bool:
    reference = component.get("reference", "")
    lib_id = component.get("lib_id", "").lower()
    value = component.get("value", "").lower()
    footprint = component.get("footprint", "").lower()
    pin_nets = " ".join(str(pin.get("net", "")) for pin in component.get("pins", [])).lower()
    text = " ".join([reference.lower(), lib_id, value, footprint, pin_nets])

    if reference.startswith(("#PWR", "TP")):
        return False
    if reference.startswith(("J", "P", "F", "SW", "S")):
        return True
    current_keywords = [
        "motor",
        "heater",
        "load",
        "battery",
        "bat",
        "vin",
        "vbus",
        "24v",
        "12v",
        "terminal",
        "connector",
        "fuse",
        "sense",
        "shunt",
        "power",
    ]
    return any(keyword in text for keyword in current_keywords)


def build_context(project: Path) -> dict[str, Any]:
    inventory = discover(project)
    schematics = []
    components = []

    for schematic in inventory["schematic_files"]:
        extracted = extract(Path(schematic))
        schematics.append(
            {
                "file": schematic,
                "counts": extracted["counts"],
                "net_count": len(extracted.get("nets", [])),
            }
        )
        for component in extracted["components"]:
            item = dict(component)
            item["schematic_file"] = schematic
            components.append(item)

    ic_candidates = [component for component in components if is_ic_candidate(component)]
    current_critical_candidates = [
        component for component in components if is_current_critical_candidate(component)
    ]
    named_nets = []
    for schematic in inventory["schematic_files"]:
        extracted = extract(Path(schematic))
        for net in extracted.get("nets", []):
            if not net.get("name", "").startswith("__unnamed_"):
                named_nets.append(
                    {
                        "schematic_file": schematic,
                        "name": net.get("name", ""),
                        "pin_count": len(net.get("pins", [])),
                        "pins": net.get("pins", []),
                    }
                )
    datasheet_links = [
        {
            "reference": component.get("reference", ""),
            "value": component.get("value", ""),
            "datasheet": component.get("datasheet", ""),
            "summary_path": str(
                Path(inventory["suggested_output_dirs"]["datasheet_cache"])
                / f"{cache_stem(component.get('value', ''), component.get('datasheet', ''))}.summary.md"
            ),
            "text_path": str(
                Path(inventory["suggested_output_dirs"]["datasheet_cache"])
                / f"{cache_stem(component.get('value', ''), component.get('datasheet', ''))}.datasheet.txt"
            ),
            "keywords_path": str(
                Path(inventory["suggested_output_dirs"]["datasheet_cache"])
                / f"{cache_stem(component.get('value', ''), component.get('datasheet', ''))}.keywords.md"
            ),
            "schematic_file": component.get("schematic_file", ""),
        }
        for component in components
        if component.get("datasheet")
    ]

    return {
        "project_root": inventory["project_root"],
        "schematics": schematics,
        "component_count": len(components),
        "ic_candidates": ic_candidates,
        "current_critical_candidates": current_critical_candidates,
        "named_nets": named_nets,
        "datasheet_links": datasheet_links,
        "suggested_output_dirs": inventory["suggested_output_dirs"],
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Build compact KiCAD review context")
    parser.add_argument("project", type=Path, help="Project directory or KiCAD file")
    parser.add_argument("--pretty", action="store_true", help="Pretty-print JSON")
    args = parser.parse_args()

    context = build_context(args.project)
    indent = 2 if args.pretty else None
    print(json.dumps(context, ensure_ascii=False, indent=indent))


if __name__ == "__main__":
    main()
