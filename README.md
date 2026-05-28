# KiCad Schematic Review Skill

This ChatGPT / OpenAI Codex skill helps review KiCad schematics with a disciplined, evidence-first workflow:

- inventory a KiCad project
- extract structured schematic facts from `.kicad_sch`
- cache and extract datasheet text
- summarize datasheets as pin-level design contracts
- review each IC, regulator, connector, and current-critical component instance
- generate Markdown review reports with explicit confidence and limitations

The current focus is schematic review. PCB layout review is intentionally out of scope for this skill version.

Recommended repository name: `kicad-schematic-review-skill`.

The requested display name can still be **KiCAD Schematic Review Skill** in GitHub's repository description. Using a lowercase hyphenated repository name avoids spaces and typos in clone/install URLs.

## What It Checks

- Component fields: reference, value, footprint, datasheet, MPN/manufacturer fields
- Pin-to-net connectivity from embedded KiCad library symbols, wires, labels, junctions, power symbols, and no-connect markers
- IC datasheet requirements, pin by pin
- Required external components such as decoupling caps, bulk caps, bootstrap/charge-pump caps, current-sense resistors, pull-ups, clocks, TVS/ESD, and configuration networks
- Power and motor/load paths, including connector and terminal current/voltage ratings
- Review gaps, parser limitations, and manual questions

## Install

Use Python 3.10+.

```bash
python3 -m venv .venv
. .venv/bin/activate
python -m pip install -r requirements.txt
```

`pypdf` is used for PDF datasheet text extraction. If you already have `pdftotext` installed, the datasheet helper can also use that as a fallback.

## Use With ChatGPT / Codex

This repository is designed to be used as a local skill directory for AI coding agents such as OpenAI Codex.

For Codex-style usage:

1. Place this folder in your local skills/plugin workspace.
2. Ask the agent to use `kicad-schematic-review` when reviewing a KiCad schematic.
3. Provide the KiCad project path and, when available, expected load current, supply voltage, checklist requirements, and known design intent.
4. The agent should follow `SKILL.md`, use the scripts in `scripts/`, and write Markdown review artifacts into the target project's `review_outputs/` directory.

Example prompt:

```text
Use the kicad-schematic-review skill to review this KiCad project.
Focus on schematic review only. Check motor driver wiring, connector current rating,
required datasheet external parts, and any missing manual-review evidence.
Project path: /path/to/project
```

## Quick Start

Inventory a project:

```bash
python scripts/inventory_project.py /path/to/KiCadProject --pretty
```

Extract schematic facts:

```bash
python scripts/extract_kicad_sch.py /path/to/project.kicad_sch --pretty
```

Build a compact review context:

```bash
python scripts/build_review_context.py /path/to/KiCadProject --pretty
```

Cache and extract a datasheet:

```bash
python scripts/datasheet_tool.py fetch "https://example.com/part.pdf" --cache-dir /path/to/KiCadProject/datasheet_cache
python scripts/datasheet_tool.py extract /path/to/KiCadProject/datasheet_cache/part.pdf --out /path/to/KiCadProject/datasheet_cache/part.datasheet.txt
python scripts/datasheet_tool.py keywords /path/to/KiCadProject/datasheet_cache/part.datasheet.txt --out /path/to/KiCadProject/datasheet_cache/part.keywords.md
```

## Review Workflow

1. Run project inventory.
2. Run schematic extraction for every schematic file that contains circuit content.
3. Identify ICs, regulators, drivers, connectors, and current-critical parts.
4. Create a datasheet summary for each unique part/package using `references/datasheet_summary_template.md`.
5. Create one instance review per IC or current-critical component using `references/ic_review_template.md`.
6. Spot-check critical extracted nets against the raw `.kicad_sch`.
7. Write the final report using `references/report_template.md`.

The scripts provide evidence. Do not treat script output as infallible; high-severity findings should be backed by extracted JSON, raw schematic evidence, and datasheet evidence.

## Important Limitations

- The schematic extractor is lightweight and dependency-free except for optional PDF handling.
- KiCad 6+ `.kicad_sch` files with embedded `lib_symbols` are the primary target.
- Hierarchical sheet connectivity is only partially represented; manually verify critical cross-sheet nets.
- The extractor is not KiCad ERC and does not replace datasheet review.
- PCB placement, routing, EMC, thermal layout, and DFM checks are outside the current scope.

## Repository Layout

```text
SKILL.md                         Codex skill instructions
requirements.txt                 Python dependencies for local deployment
scripts/inventory_project.py     Project file discovery
scripts/extract_kicad_sch.py     Schematic fact extraction
scripts/build_review_context.py  Compact context builder
scripts/datasheet_tool.py        Datasheet fetch/extract/keyword helper
references/                      Review templates and workflow notes
agents/openai.yaml               Optional agent config
```

## License

MIT. See `LICENSE`.

## 中文说明

这个 skill 目前专注于 KiCad 原理图审核，不做 PCB 布局审核。核心思路是：先提取结构化事实，再结合 datasheet 和 checklist 做逐 pin、逐器件的审核。对于电机驱动、电源、连接器、端子、采样电阻等高风险路径，要额外检查电流、电压、功耗和降额余量。

高严重度结论必须写清楚证据来源：提取 JSON、原始 `.kicad_sch`、datasheet 摘要或 datasheet 页码/章节。没有 datasheet 或没有人工 spot-check 的地方，应明确标为 `manual_review` 或低置信度。
