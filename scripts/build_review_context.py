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
from datasheet_tool import looks_like_html, looks_like_pdf, safe_name  # noqa: E402


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


def positive_voltage_from_net(name: str) -> float | None:
    match = re.fullmatch(r"\+?(\d+(?:\.\d+)?)v", name.strip().lower())
    if not match:
        return None
    return float(match.group(1))


def extract_numeric_annotations(schematic_texts: list[dict[str, Any]]) -> list[dict[str, Any]]:
    annotations: list[dict[str, Any]] = []
    patterns = [
        ("power_w", r"(?<![A-Za-z0-9.])(\d+(?:\.\d+)?)\s*w\b"),
        ("current_a", r"(?<![A-Za-z0-9.])(\d+(?:\.\d+)?)\s*a\b"),
        ("voltage_v", r"(?<![A-Za-z0-9.])(\d+(?:\.\d+)?)\s*v\b"),
    ]
    for item in schematic_texts:
        text = str(item.get("text", ""))
        lower = text.lower()
        for kind, pattern in patterns:
            for match in re.finditer(pattern, lower):
                annotations.append(
                    {
                        "kind": kind,
                        "value": float(match.group(1)),
                        "text": text,
                        "schematic_file": item.get("schematic_file", ""),
                        "position": item.get("position"),
                    }
                )
    return annotations


def infer_motor_load_count(named_nets: list[dict[str, Any]], components: list[dict[str, Any]]) -> int:
    motor_prefixes: set[str] = set()
    for net in named_nets:
        name = str(net.get("name", ""))
        match = re.match(r"^(motor[^+-]*)([+-])$", name, flags=re.IGNORECASE)
        if match:
            motor_prefixes.add(match.group(1).lower())
    if motor_prefixes:
        return len(motor_prefixes)
    driver_count = sum(
        1
        for component in components
        if "motor" in " ".join(
            str(component.get(key, "")) for key in ["lib_id", "value", "description"]
        ).lower()
        and str(component.get("reference", "")).startswith("U")
    )
    return max(1, driver_count)


def build_design_intent(
    components: list[dict[str, Any]],
    named_nets: list[dict[str, Any]],
    schematic_texts: list[dict[str, Any]],
) -> dict[str, Any]:
    annotations = extract_numeric_annotations(schematic_texts)
    rails = [
        {"name": net.get("name", ""), "voltage_v": voltage}
        for net in named_nets
        for voltage in [positive_voltage_from_net(str(net.get("name", "")))]
        if voltage is not None
    ]
    positive_rails = [rail["voltage_v"] for rail in rails if rail["voltage_v"] > 0]
    selected_voltage = max(positive_rails) if positive_rails else None
    motor_load_count = infer_motor_load_count(named_nets, components)

    current_estimates: list[dict[str, Any]] = []
    for annotation in annotations:
        if annotation["kind"] != "power_w" or selected_voltage is None:
            continue
        per_load_current = annotation["value"] / selected_voltage
        load_count = motor_load_count if "motor" in str(annotation.get("text", "")).lower() else 1
        current_estimates.append(
            {
                "basis": annotation,
                "voltage_v": selected_voltage,
                "load_count": load_count,
                "per_load_current_a": per_load_current,
                "total_current_a": per_load_current * load_count,
                "assumption": (
                    "Computed from schematic power annotation and highest positive voltage rail; "
                    "startup/stall/transient current is not included."
                ),
            }
        )

    return {
        "annotations": annotations,
        "voltage_rails": rails,
        "inferred_motor_load_count": motor_load_count,
        "current_estimates": current_estimates,
    }


def classify_cached_file(path: Path) -> str:
    if not path.exists() or path.stat().st_size == 0:
        return "missing"
    if path.suffix.lower() in {".txt", ".md"}:
        return "text"
    data = path.read_bytes()[:4096]
    if looks_like_pdf(data):
        return "pdf"
    if looks_like_html(data):
        return "html_wrapper"
    return "unknown"


def datasheet_cache_status(datasheet_links: list[dict[str, Any]], cache_dir: Path) -> list[dict[str, Any]]:
    statuses: list[dict[str, Any]] = []
    for link in datasheet_links:
        source = str(link.get("datasheet", ""))
        cached_source = cache_dir / safe_name(source)
        source_type = classify_cached_file(cached_source)
        summary_path = Path(str(link.get("summary_path", "")))
        text_path = Path(str(link.get("text_path", "")))
        keywords_path = Path(str(link.get("keywords_path", "")))
        warnings: list[str] = []
        if source_type == "html_wrapper":
            warnings.append("Cached source is HTML, not a resolved datasheet PDF.")
        if not summary_path.exists():
            warnings.append("No datasheet summary file found at the expected path.")
        statuses.append(
            {
                "reference": link.get("reference", ""),
                "value": link.get("value", ""),
                "datasheet": source,
                "cached_source_path": str(cached_source),
                "cached_source_type": source_type,
                "summary_exists": summary_path.exists(),
                "text_exists": text_path.exists(),
                "keywords_exists": keywords_path.exists(),
                "warnings": warnings,
            }
        )
    return statuses


def pcb_status(pcb_files: list[str]) -> list[dict[str, Any]]:
    statuses: list[dict[str, Any]] = []
    for pcb_file in pcb_files:
        path = Path(pcb_file)
        text = path.read_text(encoding="utf-8", errors="replace") if path.exists() else ""
        counts = {
            "footprints": len(re.findall(r"\(footprint\b", text)),
            "segments": len(re.findall(r"\(segment\b", text)),
            "vias": len(re.findall(r"\(via\b", text)),
            "zones": len(re.findall(r"\(zone\b", text)),
        }
        statuses.append(
            {
                "file": pcb_file,
                "exists": path.exists(),
                "line_count": len(text.splitlines()) if text else 0,
                "counts": counts,
                "is_effectively_empty": path.exists() and not any(counts.values()),
                "review_note": (
                    "PCB has no placed/routed evidence; trace width, thermal, copper, via, "
                    "clearance, and EMI checks must remain manual_review."
                    if path.exists() and not any(counts.values())
                    else ""
                ),
            }
        )
    return statuses


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
            references / "checklists" / "dcdc_bringup_test.md",
            [
                "ripple",
                "load step",
                "load-step",
                "efficiency",
                "short circuit",
                "short-circuit",
                "hiccup",
                "line regulation",
                "load regulation",
                "sw waveform",
                "switching waveform",
                "thermal test",
                "mp4560",
            ],
            "DCDC validation, ripple, efficiency, transient, or protection-test evidence found.",
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
            references / "checklists" / "current_sensing.md",
            [
                "current sense",
                "current-sense",
                "current sensing",
                "shunt",
                "isense",
                "isen",
                "csa",
                "cs+",
                "cs-",
                "sense+",
                "sense-",
                "spx",
                "snx",
                "ipropi",
                "ina180",
                "ina181",
                "ina240",
                "ina250",
                "ina226",
                "hall current",
                "phase current",
                "low-side current",
                "high-side current",
            ],
            "Current-sense, shunt, CSA, Hall, or phase-current feedback evidence found.",
        ),
        (
            references / "checklists" / "motor_control_foc.md",
            [
                "foc",
                "svpwm",
                "pmsm",
                "bldc",
                "acim",
                "three-phase",
                "3-phase",
                "phase current",
                "encoder",
                "resolver",
                "hall sensor",
                "electrical angle",
                "dead time",
                "dead-time",
                "instaspin",
            ],
            "FOC, three-phase motor control, phase-current sampling, or position-feedback evidence found.",
        ),
        (
            references / "checklists" / "signal_power_integrity.md",
            [
                "signal integrity",
                "power integrity",
                "impedance",
                "transmission line",
                "differential",
                "usb",
                "ethernet",
                "rs485",
                "can bus",
                "canh",
                "canl",
                "clock",
                "crystal",
                "oscillator",
                "esd",
                "emi",
                "emc",
                "termination",
            ],
            "Signal-integrity, power-integrity, differential interface, clock, or EMC evidence found.",
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
    design_intent = build_design_intent(components, named_nets, schematic_texts)
    cache_dir = Path(inventory["suggested_output_dirs"]["datasheet_cache"])

    return {
        "project_root": inventory["project_root"],
        "schematics": schematics,
        "component_count": len(components),
        "ic_candidates": ic_candidates,
        "current_critical_candidates": current_critical_candidates,
        "named_nets": named_nets,
        "schematic_texts": schematic_texts,
        "design_intent": design_intent,
        "checklists": checklists,
        "datasheet_links": datasheet_links,
        "datasheet_cache_status": datasheet_cache_status(datasheet_links, cache_dir),
        "pcb_status": pcb_status(inventory["pcb_files"]),
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
