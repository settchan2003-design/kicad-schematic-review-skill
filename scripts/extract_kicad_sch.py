#!/usr/bin/env python3
"""Extract structured facts from a KiCAD .kicad_sch file.

The extractor is intentionally dependency-light. It is not a replacement for
KiCad ERC or a full electrical rule engine; it builds a factual review context:
components, library pins, approximate pin-net mapping, labels, wires, and
no-connect markers. The reviewer should still spot-check critical nets against
the raw schematic and datasheets before making final claims.
"""

from __future__ import annotations

import argparse
import json
import math
from pathlib import Path
from typing import Any

EPSILON_MM = 0.03


def tokenize(text: str) -> list[str]:
    tokens: list[str] = []
    i = 0
    while i < len(text):
        ch = text[i]
        if ch.isspace():
            i += 1
            continue
        if ch in "()":
            tokens.append(ch)
            i += 1
            continue
        if ch == '"':
            i += 1
            value = []
            while i < len(text):
                if text[i] == "\\" and i + 1 < len(text):
                    value.append(text[i + 1])
                    i += 2
                    continue
                if text[i] == '"':
                    i += 1
                    break
                value.append(text[i])
                i += 1
            tokens.append("".join(value))
            continue
        start = i
        while i < len(text) and not text[i].isspace() and text[i] not in "()":
            i += 1
        tokens.append(text[start:i])
    return tokens


def parse_expr(tokens: list[str], index: int = 0) -> tuple[Any, int]:
    if tokens[index] != "(":
        return tokens[index], index + 1

    index += 1
    expr: list[Any] = []
    while index < len(tokens) and tokens[index] != ")":
        item, index = parse_expr(tokens, index)
        expr.append(item)

    if index >= len(tokens):
        raise ValueError("Unbalanced parentheses in schematic file")
    return expr, index + 1


def parse_sexpr(text: str) -> Any:
    tokens = tokenize(text)
    parsed, index = parse_expr(tokens)
    if index != len(tokens):
        raise ValueError("Unexpected tokens after first S-expression")
    return parsed


def children(expr: list[Any], name: str) -> list[list[Any]]:
    return [item for item in expr[1:] if isinstance(item, list) and item and item[0] == name]


def first_atom(expr: list[Any], name: str, default: str = "") -> str:
    for item in children(expr, name):
        if len(item) > 1 and isinstance(item[1], str):
            return item[1]
    return default


def all_deep(expr: Any, name: str) -> list[list[Any]]:
    found: list[list[Any]] = []
    if isinstance(expr, list):
        if expr and expr[0] == name:
            found.append(expr)
        for item in expr[1:]:
            found.extend(all_deep(item, name))
    return found


def property_map(symbol: list[Any]) -> dict[str, str]:
    props: dict[str, str] = {}
    for item in children(symbol, "property"):
        if len(item) >= 3 and isinstance(item[1], str) and isinstance(item[2], str):
            props[item[1]] = item[2]
    return props


def first_non_empty_property(props: dict[str, str], names: list[str]) -> str:
    normalized = {key.lower().replace(" ", "").replace("_", ""): value for key, value in props.items()}
    for name in names:
        value = normalized.get(name.lower().replace(" ", "").replace("_", ""), "")
        if value:
            return value
    return ""


def point_from(expr: list[Any], name: str) -> list[float] | None:
    item = next(iter(children(expr, name)), None)
    if not item or len(item) < 3:
        return None
    try:
        return [float(item[1]), float(item[2])]
    except ValueError:
        return None


def at_from(expr: list[Any]) -> tuple[float, float, float]:
    item = next(iter(children(expr, "at")), None)
    if not item or len(item) < 3:
        return (0.0, 0.0, 0.0)
    try:
        angle = float(item[3]) if len(item) > 3 else 0.0
        return (float(item[1]), float(item[2]), angle)
    except ValueError:
        return (0.0, 0.0, 0.0)


def xy_points(expr: list[Any]) -> list[tuple[float, float]]:
    pts = next(iter(children(expr, "pts")), None)
    if not pts:
        return []
    points = []
    for item in children(pts, "xy"):
        if len(item) >= 3:
            try:
                points.append((float(item[1]), float(item[2])))
            except ValueError:
                continue
    return points


def coord_key(x: float, y: float) -> tuple[int, int]:
    return (round(x / EPSILON_MM), round(y / EPSILON_MM))


def point_on_segment(point: tuple[float, float], a: tuple[float, float], b: tuple[float, float]) -> bool:
    px, py = point
    ax, ay = a
    bx, by = b
    if px < min(ax, bx) - EPSILON_MM or px > max(ax, bx) + EPSILON_MM:
        return False
    if py < min(ay, by) - EPSILON_MM or py > max(ay, by) + EPSILON_MM:
        return False
    dx = bx - ax
    dy = by - ay
    if abs(dx) < EPSILON_MM and abs(dy) < EPSILON_MM:
        return math.hypot(px - ax, py - ay) <= EPSILON_MM
    return abs((px - ax) * dy - (py - ay) * dx) <= EPSILON_MM * max(abs(dx), abs(dy), 1.0)


class UnionFind:
    def __init__(self) -> None:
        self.parent: dict[tuple[int, int], tuple[int, int]] = {}

    def add(self, item: tuple[int, int]) -> None:
        self.parent.setdefault(item, item)

    def find(self, item: tuple[int, int]) -> tuple[int, int]:
        self.add(item)
        parent = self.parent[item]
        if parent != item:
            self.parent[item] = self.find(parent)
        return self.parent[item]

    def union(self, left: tuple[int, int], right: tuple[int, int]) -> None:
        left_root = self.find(left)
        right_root = self.find(right)
        if left_root != right_root:
            self.parent[right_root] = left_root


def parse_pin(pin: list[Any]) -> dict[str, Any] | None:
    if len(pin) < 2:
        return None
    pin_type = str(pin[1])
    x, y, angle = at_from(pin)
    name_node = next(iter(children(pin, "name")), None)
    number_node = next(iter(children(pin, "number")), None)
    return {
        "name": name_node[1] if name_node and len(name_node) > 1 else "",
        "pin_number": number_node[1] if number_node and len(number_node) > 1 else "",
        "type": pin_type,
        "relative_position": [x, y],
        "angle": angle,
    }


def lib_symbol_pin_map(root: list[Any]) -> dict[str, list[dict[str, Any]]]:
    result: dict[str, list[dict[str, Any]]] = {}
    for lib_symbols in children(root, "lib_symbols"):
        for symbol in children(lib_symbols, "symbol"):
            if len(symbol) < 2 or not isinstance(symbol[1], str):
                continue
            lib_id = symbol[1]
            pins = []
            seen = set()
            for pin in all_deep(symbol, "pin"):
                parsed = parse_pin(pin)
                if not parsed:
                    continue
                key = (parsed["pin_number"], parsed["name"], tuple(parsed["relative_position"]))
                if key in seen:
                    continue
                seen.add(key)
                pins.append(parsed)
            result[lib_id] = pins
    return result


def transform_pin(origin: tuple[float, float, float], relative: list[float]) -> list[float]:
    ox, oy, angle = origin
    px, py = relative
    radians = math.radians(angle % 360)
    x = px * math.cos(radians) - py * math.sin(radians)
    y = px * math.sin(radians) + py * math.cos(radians)
    return [round(ox + x, 4), round(oy - y, 4)]


def extract(path: Path) -> dict[str, Any]:
    root = parse_sexpr(path.read_text(encoding="utf-8"))
    if not isinstance(root, list) or not root or root[0] != "kicad_sch":
        raise ValueError(f"{path} does not look like a KiCAD schematic")

    lib_symbols = children(root, "lib_symbols")
    lib_pins = lib_symbol_pin_map(root)
    symbols = [
        item
        for item in children(root, "symbol")
        if not (len(item) > 1 and isinstance(item[1], str))
    ]

    components = []
    pin_points: list[dict[str, Any]] = []
    for symbol in symbols:
        props = property_map(symbol)
        datasheet = props.get("Datasheet", "")
        lib_id = first_atom(symbol, "lib_id")
        origin = at_from(symbol)
        pins = []
        for pin in lib_pins.get(lib_id, []):
            abs_pos = transform_pin(origin, pin["relative_position"])
            pin_item = {
                "number": pin["pin_number"],
                "name": pin["name"],
                "type": pin["type"],
                "position": abs_pos,
            }
            pins.append(pin_item)
            pin_points.append(
                {
                    "reference": props.get("Reference", ""),
                    "pin_number": pin["pin_number"],
                    "pin_name": pin["name"],
                    "pin_type": pin["type"],
                    "position": abs_pos,
                    "lib_id": lib_id,
                }
            )
        components.append(
            {
                "lib_id": lib_id,
                "reference": props.get("Reference", ""),
                "value": props.get("Value", ""),
                "footprint": props.get("Footprint", ""),
                "datasheet": datasheet,
                "datasheet_source": "Datasheet" if datasheet else "",
                "part_number": first_non_empty_property(
                    props,
                    [
                        "MPN",
                        "Manufacturer Part Number",
                        "Part Number",
                        "Supplier Part",
                        "LCSC",
                    ],
                ),
                "manufacturer": first_non_empty_property(props, ["Manufacturer", "MFR"]),
                "description": props.get("Description", ""),
                "properties": props,
                "position": point_from(symbol, "at"),
                "in_bom": first_atom(symbol, "in_bom", "unknown"),
                "on_board": first_atom(symbol, "on_board", "unknown"),
                "dnp": first_atom(symbol, "dnp", "unknown"),
                "pins": pins,
            }
        )

    wires = [{"points": xy_points(wire)} for wire in children(root, "wire") if len(xy_points(wire)) >= 2]
    labels = []
    for label_type in ["label", "global_label", "hierarchical_label"]:
        for label in children(root, label_type):
            at = point_from(label, "at")
            if len(label) > 1 and isinstance(label[1], str) and at:
                labels.append({"name": label[1], "type": label_type, "position": at})
    junctions = [point_from(junction, "at") for junction in children(root, "junction")]
    junctions = [point for point in junctions if point]
    no_connects = [point_from(nc, "at") for nc in children(root, "no_connect")]
    no_connects = [point for point in no_connects if point]

    union = UnionFind()
    points_with_names: list[tuple[tuple[int, int], str]] = []
    for wire in wires:
        keys = [coord_key(x, y) for x, y in wire["points"]]
        for key in keys:
            union.add(key)
        for key in keys[1:]:
            union.union(keys[0], key)
    for point in junctions + no_connects:
        union.add(coord_key(point[0], point[1]))
    for pin in pin_points:
        key = coord_key(pin["position"][0], pin["position"][1])
        union.add(key)
        for wire in wires:
            if point_on_segment((pin["position"][0], pin["position"][1]), wire["points"][0], wire["points"][-1]):
                union.union(key, coord_key(wire["points"][0][0], wire["points"][0][1]))
    named_label_keys: dict[str, tuple[int, int]] = {}
    for label in labels:
        key = coord_key(label["position"][0], label["position"][1])
        union.add(key)
        points_with_names.append((key, label["name"]))
        if label["name"] in named_label_keys:
            union.union(named_label_keys[label["name"]], key)
        else:
            named_label_keys[label["name"]] = key
        for wire in wires:
            if point_on_segment((label["position"][0], label["position"][1]), wire["points"][0], wire["points"][-1]):
                union.union(key, coord_key(wire["points"][0][0], wire["points"][0][1]))
    named_power_keys: dict[str, tuple[int, int]] = {}
    for component in components:
        if component["lib_id"].startswith("power:"):
            value = component["value"]
            for pin in component["pins"]:
                key = coord_key(pin["position"][0], pin["position"][1])
                points_with_names.append((key, value))
                if value in named_power_keys:
                    union.union(named_power_keys[value], key)
                else:
                    named_power_keys[value] = key

    root_names: dict[tuple[int, int], list[str]] = {}
    for key, name in points_with_names:
        root_names.setdefault(union.find(key), [])
        if name not in root_names[union.find(key)]:
            root_names[union.find(key)].append(name)

    nets_by_root: dict[tuple[int, int], dict[str, Any]] = {}
    for pin in pin_points:
        key = coord_key(pin["position"][0], pin["position"][1])
        root_key = union.find(key)
        names = root_names.get(root_key, [])
        net_name = names[0] if names else f"__unnamed_{len(nets_by_root) + 1}"
        net = nets_by_root.setdefault(root_key, {"name": net_name, "aliases": names, "pins": []})
        net["pins"].append(
            {
                "component": pin["reference"],
                "pin_number": pin["pin_number"],
                "pin_name": pin["pin_name"],
                "pin_type": pin["pin_type"],
            }
        )
        pin["net"] = net_name

    pin_net_map: dict[str, list[dict[str, Any]]] = {}
    for pin in pin_points:
        pin_net_map.setdefault(pin["reference"], []).append(
            {
                "pin_number": pin["pin_number"],
                "pin_name": pin["pin_name"],
                "pin_type": pin["pin_type"],
                "net": pin.get("net", ""),
                "position": pin["position"],
            }
        )
    for component in components:
        if component["reference"] in pin_net_map:
            component["pins"] = pin_net_map[component["reference"]]

    counts = {
        "components": len(components),
        "lib_symbols": len(lib_symbols[0]) - 1 if lib_symbols else 0,
        "wires": len(children(root, "wire")),
        "junctions": len(children(root, "junction")),
        "labels": len(children(root, "label")),
        "global_labels": len(children(root, "global_label")),
        "hierarchical_labels": len(children(root, "hierarchical_label")),
        "no_connects": len(children(root, "no_connect")),
        "sheets": len(children(root, "sheet")),
    }

    return {
        "file": str(path),
        "version": first_atom(root, "version"),
        "generator": first_atom(root, "generator"),
        "uuid": first_atom(root, "uuid"),
        "paper": first_atom(root, "paper"),
        "counts": counts,
        "components": components,
        "nets": sorted(nets_by_root.values(), key=lambda item: item["name"]),
        "labels": labels,
        "wires": wires,
        "junctions": junctions,
        "no_connects": no_connects,
        "extraction_notes": [
            "Pin positions are computed from embedded lib_symbols and symbol placement.",
            "Net mapping joins wires, labels, power symbols, junctions, and pins using coordinate matching.",
            "Hierarchical sheet connectivity is not fully resolved by this lightweight extractor; spot-check multi-sheet critical nets.",
        ],
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Extract facts from a KiCAD schematic")
    parser.add_argument("schematic", type=Path, help="Path to a .kicad_sch file")
    parser.add_argument("--pretty", action="store_true", help="Pretty-print JSON")
    args = parser.parse_args()

    data = extract(args.schematic)
    indent = 2 if args.pretty else None
    print(json.dumps(data, ensure_ascii=False, indent=indent))


if __name__ == "__main__":
    main()
