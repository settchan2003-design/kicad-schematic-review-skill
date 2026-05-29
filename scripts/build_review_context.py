#!/usr/bin/env python3
"""Build a compact review context for a KiCAD project."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
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


def parse_checklist_items(path: Path) -> list[str]:
    items: list[str] = []
    for line in path.read_text(encoding="utf-8", errors="replace").splitlines():
        match = re.match(r"^\s*-\s+(?:\[[ xX]\]\s*)?(.+?)\s*$", line)
        if match and match.group(1):
            items.append(match.group(1))
    return items


def discover_project_checklists(project_root: Path) -> list[Path]:
    candidates: list[Path] = []
    names = [
        "review_checklist.md",
        "schematic_checklist.md",
        "checklist.md",
        "hardware_checklist.md",
    ]
    for name in names:
        path = project_root / name
        if path.exists():
            candidates.append(path)
    for path in sorted(project_root.glob("*checklist*.md")):
        if path not in candidates:
            candidates.append(path)
    return candidates


def checklist_entry(path: Path, source: str, applies: bool, reason: str) -> dict[str, Any]:
    items = parse_checklist_items(path)
    return {
        "path": str(path),
        "source": source,
        "applies": applies,
        "reason": reason,
        "item_count": len(items),
        "items": items,
    }


def discover_checklists(
    project_root: Path,
    components: list[dict[str, Any]],
    named_nets: list[dict[str, Any]],
    schematic_texts: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    skill_root = SCRIPT_DIR.parent
    references = skill_root / "references"
    text_blob = " ".join(
        [
            " ".join(str(component.get(key, "")) for key in ["reference", "lib_id", "value", "description"])
            for component in components
        ]
        + [str(net.get("name", "")) for net in named_nets]
        + [str(item.get("text", "")) for item in schematic_texts]
    ).lower()

    checklists: list[dict[str, Any]] = []
    core = references / "checklist_example.md"
    if core.exists():
        checklists.append(
            checklist_entry(
                core,
                "skill_core",
                True,
                "Baseline schematic review checklist; always apply unless a project checklist supersedes an item.",
            )
        )

    domain_rules = [
        (
            references / "checklists" / "motor_driver.md",
            ["motor", "drv", "h-bridge", "bridge", "driver_motor"],
            "Motor-driver, H-bridge, or motor-load evidence found.",
        ),
        (
            references / "checklists" / "connector_power.md",
            ["connector", "terminal", "jst", "wj", "24v", "12v", "vin", "vbus", "motor"],
            "Connector, terminal, supply rail, or load-current evidence found.",
        ),
        (
            references / "checklists" / "dcdc.md",
            [
                "dcdc",
                "dc-dc",
                "buck",
                "boost",
                "fly-buck",
                "flybuck",
                "converter",
                "regulator",
                "switching",
                "lm5017",
                "lm5007",
                "lm5008",
                "lm5009",
                "lm5010",
                "cot",
                "constant on-time",
            ],
            "Switching regulator or DCDC evidence found.",
        ),
        (
            references / "checklists" / "half_bridge_gate_drive.md",
            [
                "half bridge",
                "half-bridge",
                "h-bridge",
                "mosfet",
                "igbt",
                "sic",
                "gate driver",
                "gatedriver",
                "bootstrap",
                "bst",
                "vgs",
                "gha",
                "ghb",
                "ghc",
                "gla",
                "glb",
                "glc",
                "high-side",
                "low-side",
                "phase",
                "uvw",
                "inverter",
                "ucc21220",
            ],
            "Half-bridge, external switch, bootstrap, or gate-driver evidence found.",
        ),
        (
            references / "checklists" / "power_entry_inrush.md",
            [
                "battery",
                "bat",
                "dc bus",
                "power bus",
                "precharge",
                "inrush",
                "soft start",
                "soft-start",
                "hot swap",
                "hotswap",
                "relay",
                "ssr",
                "solid state",
                "solid-state",
                "fuse",
                "24v",
                "48v",
                "bulk",
                "2000uf",
            ],
            "Power-entry, bus capacitance, relay, fuse, or inrush evidence found.",
        ),
        (
            references / "checklists" / "mcu_adc.md",
            [
                "mcu",
                "microcontroller",
                "stm32",
                "esp32",
                "adc",
                "ain",
                "vref",
                "vcap",
                "swd",
                "jtag",
                "boot0",
                "nrst",
                "reset",
                "xtal",
                "osc",
                "crystal",
                "sensor",
            ],
            "MCU, ADC, reference, reset, boot, clock, or low-level signal evidence found.",
        ),
    ]
    for path, keywords, reason in domain_rules:
        if path.exists() and any(keyword in text_blob for keyword in keywords):
            checklists.append(checklist_entry(path, "skill_domain", True, reason))

    for path in discover_project_checklists(project_root):
        checklists.append(
            checklist_entry(
                path,
                "project",
                True,
                "Project-local checklist discovered by filename.",
            )
        )
    return checklists


def build_context(project: Path) -> dict[str, Any]:
    inventory = discover(project)
    schematics = []
    components = []
    schematic_texts = []

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
        for text_item in extracted.get("texts", []):
            item = dict(text_item)
            item["schematic_file"] = schematic
            schematic_texts.append(item)

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
    checklists = discover_checklists(
        Path(inventory["project_root"]),
        components,
        named_nets,
        schematic_texts,
    )

    return {
        "project_root": inventory["project_root"],
        "schematics": schematics,
        "component_count": len(components),
        "ic_candidates": ic_candidates,
        "current_critical_candidates": current_critical_candidates,
        "named_nets": named_nets,
        "schematic_texts": schematic_texts,
        "checklists": checklists,
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
