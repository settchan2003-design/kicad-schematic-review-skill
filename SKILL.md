---
name: kicad-schematic-review
description: Review KiCAD schematic projects using structured schematic extraction, component Datasheet links, user checklists, pin-level datasheet summaries, per-IC connection reviews, and current-path rating checks.
---

# KiCAD Schematic Review

Use this skill when the user asks to review a KiCAD schematic, validate IC wiring against datasheets, apply a hardware checklist, or generate a schematic review report.

## Core Idea

Do not review a large board by loading every schematic and datasheet at once. Work in stages, and keep a hard boundary between extracted facts and engineering judgement:

1. Inventory the KiCAD project.
2. Extract structured schematic facts: components, pins, nets, labels, no-connects, and datasheet fields.
3. Spot-check critical extracted facts against the raw `.kicad_sch` before making high-confidence claims.
4. Identify ICs, regulators, connectors, and current-carrying parts with `Datasheet` links.
5. Build one reusable datasheet summary per part/package.
6. Review one schematic IC or current-critical instance at a time.
7. Merge per-instance findings into a final report with explicit confidence and review gaps.

## Schematic Review Contract

A schematic review is not complete after running the scripts. The scripts create evidence; the reviewer must still compare that evidence with datasheets, the raw schematic, and the user's checklist.

Minimum bar for an actual review:

- Run `inventory_project.py`.
- Run `extract_kicad_sch.py` on every `.kicad_sch` that contains design content.
- Confirm component count and the reviewed IC pin maps against raw schematic snippets for critical parts.
- Check every IC/regulator/driver supply pin, ground pin, enable/reset/boot/mode pin, output/load pin, sense/reference pin, and exposed pad.
- Check required external parts from the datasheet: decoupling, bulk capacitance, bootstrap/charge-pump capacitors, sense resistors, pull-ups/downs, snubbers, TVS/ESD, clocks/crystals, and configuration networks.
- Check connector/terminal/fuse/current-sense ratings for any motor, heater, actuator, battery, high-current, or user-provided load path.
- State which datasheets were verified, which were missing, and which conclusions are only schematic-consistency observations.
- Do not use words like "verified" or "per datasheet" unless the report cites a datasheet summary or direct datasheet evidence.

## Inputs

- KiCAD project directory, `.kicad_pro`, or `.kicad_sch`.
- User checklist file or checklist text.
- Datasheet URLs or paths in component properties, especially `Datasheet`.
- Optional output path. Default to `schematic_review.md` in the project directory.

## Required Workflow

1. Run `scripts/inventory_project.py <project> --pretty`.
   - Find `.kicad_pro`, `.kicad_sch`, and `.kicad_pcb`.
   - Treat local datasheet files as optional fallback only.

2. Run `scripts/extract_kicad_sch.py <schematic> --pretty` for each schematic.
   - Use the JSON as the factual basis.
   - Read `components[].pins[]` for pin-to-net facts.
   - Read `nets[]` for net-level connectivity.
   - Preserve `extraction_notes` in the final parser limitations.
   - Preserve component custom properties such as `Datasheet`, `MPN`, `Manufacturer`, `LCSC`, and supplier fields.
   - If a schematic has hierarchical sheets, spot-check cross-sheet nets manually; this lightweight extractor reports the limitation explicitly.

3. Identify IC candidates.
   - References beginning with `U`.
   - IC-like library IDs or checklist-specified parts.
   - Parts with meaningful datasheet links and multi-pin functional behavior.
   - Always include motor drivers, regulators, MCUs, sensors, level shifters, communication transceivers, ADC/DACs, protection ICs, and power-management ICs.
   - Also identify current-critical non-IC parts: connectors, terminal blocks, fuses, switches, shunts, load resistors, motors/loads, cables, and protection parts.

4. Resolve datasheet source.
   - Prefer the component `Datasheet` property.
   - Accept HTTP(S) URLs, absolute paths, and project-relative paths.
   - If missing, inspect custom fields such as `MPN`, `Manufacturer Part Number`, `Part Number`, `LCSC`, `Supplier Part`, and `URL`.
   - If still missing, mark as `manual_review`.

5. Create or update `datasheet_cache/<part>.summary.md`.
   - Use `references/datasheet_summary_template.md`.
   - If the project has a local `.venv`, prefer `.venv/bin/python` when running datasheet tools so PDF parsing dependencies are available.
   - Use `scripts/datasheet_tool.py fetch <datasheet-url-or-path> --cache-dir <project>/datasheet_cache` to cache URL-based datasheets when needed. The fetch command reuses cached files first; add `--offline` to fail instead of downloading on a cache miss, or `--verbose` to show cache-hit/download status on stderr.
   - Use `scripts/datasheet_tool.py extract <cached-pdf-or-local-file> --out <project>/datasheet_cache/<part>.datasheet.txt` to produce searchable text when a PDF text extractor is available.
   - Use `scripts/datasheet_tool.py keywords <text-file> --out <project>/datasheet_cache/<part>.keywords.md` to create a compact reading map before summarizing.
   - This file is the datasheet-side design contract.
   - Expand every physical pin for the reviewed package.
   - Capture required/allowed connection, required external parts, recommended values, placement/layout notes, unused-pin rules, and evidence.
   - For motor drivers and power ICs, explicitly capture bulk capacitance, bootstrap/charge-pump capacitors, current-sense parts, snubbers, TVS/ESD, thermal pad guidance, and supply limits.
   - For connectors, terminals, fuses, switches, cables, and current-carrying passives, explicitly capture current rating, voltage rating, wire gauge, contact resistance, temperature range, pitch/package, and derating notes.
   - If PDF text extraction is unavailable, tell the user to install `pypdf` or provide extracted datasheet text, then continue with available schematic-only checks.
   - Mark the summary status as `verified` only after pin table, recommended operating conditions, application circuit, and package-specific notes were checked.
   - If the datasheet text extraction is weak or missing tables, mark affected fields as `needs-human-check`.

6. Perform raw schematic spot-checks before instance reviews.
   - For every high-severity finding candidate, open the raw `.kicad_sch` around the affected symbol/label/wire and confirm the extracted connection.
   - For every reviewed IC, verify at least power pins, ground pins, output pins, sense/reference pins, and any suspicious unnamed nets.
   - If extracted pin positions or net names conflict with visual/raw evidence, trust the raw schematic and describe the parser issue.

7. Review current-carrying paths before final sign-off.
   - Identify power entry, motor outputs, load connectors, fuses, switches, sense resistors, and terminal blocks.
   - Estimate current from known or user-provided power: `I = P / V`, then add efficiency and transient/startup margin when relevant.
   - Compare estimated continuous and peak current against connector/contact/wire/fuse/resistor ratings.
   - Flag any path with no derating margin, unknown rating, or rating below expected current.
   - For motor outputs, consider current limit and startup/stall current, not only average electrical power.

8. Create one review file per IC or current-critical instance in `review_outputs/`.
   - Use `references/ic_review_template.md`.
   - Compare expected datasheet requirements against actual schematic connections pin by pin.
   - Keep required external component checks separate from pin-net checks.
   - One datasheet summary may be reused by multiple IC instances, but each instance gets its own review file.
   - Include a confidence value for each finding: high, medium, or low.
   - Include evidence source for each finding: extracted JSON, raw schematic, datasheet summary, direct datasheet page/section, or user checklist.

9. Generate the final report.
   - Use `references/report_template.md`.
   - Lead with high-severity findings.
   - Include checklist status, per-IC summary, manual-review questions, and parser limitations.
   - Include a "Verification Basis" section listing scripts run, datasheets summarized, raw spot-checks performed, and skipped checks.

## Result Labels

- `pass`: Clearly satisfies the requirement.
- `fail`: Clearly violates the requirement.
- `warning`: Risky, incomplete, or materially different from recommendation.
- `manual_review`: Not enough information in the available files.

## Context Rules

- Load only one IC datasheet context at a time.
- Cache datasheet knowledge in `datasheet_cache/`.
- Cache instance findings in `review_outputs/`.
- When context is tight, keep only current IC facts, its datasheet summary, relevant checklist items, and active findings.
- Treat script JSON as review evidence, not as infallible truth.
- Prefer small, auditable review files over one giant report.

## Datasheet Analysis Rules

- The datasheet summary must be pin-centric, not a generic overview.
- Every physical pin in the package should appear in `Pin-Level Requirements`.
- When the datasheet gives a typical application circuit, convert it into explicit required/recommended external component checks.
- Distinguish hard requirements from recommendations and example-only values.
- Keep source evidence short: page, section, table, or figure names are enough.
- For repeated ICs, summarize the datasheet once and review each schematic instance separately.
- Do not limit datasheet review to ICs. Any component carrying load current or setting a safety limit must be reviewed against ratings.

## Power Path Rules

- Always check connector and terminal current rating when a net name or checklist implies supply, motor, heater, actuator, battery, or other power path.
- If output/load power is known, compute input/load current and compare with connector rating.
- If power is not known but a motor driver, regulator, fuse, or terminal is present, ask for expected continuous/peak load current and still report missing rating evidence as `manual_review`.
- Treat average current, startup/stall current, RMS current, temperature rise, wire gauge, and number of contacts used in parallel as separate concerns.
- Use at least a warning when estimated current exceeds 70% of a connector/contact rating unless the checklist specifies another derating rule.
- Use fail when estimated continuous current exceeds the connector/contact rating.

## Output Rules

- Prefer Markdown reports.
- Use concrete evidence: reference designators, pin numbers, net names, component values, datasheet summary paths, and schematic file paths.
- Do not give vague hardware advice. Every issue should explain why it matters and what to check or change.
- If pin-net extraction or datasheet access is incomplete, say so explicitly.
- Each final finding should include severity, confidence, evidence, impact, and a practical recommendation.
- Separate blockers/failures from warnings, assumptions, and manual-review questions.
