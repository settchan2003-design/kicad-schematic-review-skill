# KiCad Schematic Review Skill

This is a ChatGPT / OpenAI Codex skill for reviewing KiCad schematics with an evidence-first hardware review workflow. It is not meant to replace KiCad ERC, and it is not a one-click claim that a design is correct. Its job is to separate the review into traceable evidence:

1. Extract structured facts from the KiCad project.
2. Turn datasheets into pin-level design contracts.
3. Review ICs, connectors, terminals, and power paths instance by instance.
4. Produce Markdown reports with findings, evidence, confidence, and manual-review gaps.

The current version focuses on **schematic review**. PCB routing, thermal layout, EMC, and DFM are treated as follow-up review items unless the relevant PCB evidence exists.

## What This Project Does

Hardware reviews often get muddy because different evidence types are mixed together: extracted nets, datasheet requirements, engineering judgment, and user-specific checklist rules. This skill keeps those sources separate so every conclusion can be traced back to evidence.

It helps an agent:

- Inventory KiCad project files such as `.kicad_pro`, `.kicad_sch`, and `.kicad_pcb`
- Extract components, pins, nets, labels, no-connect markers, and schematic free-text annotations
- Identify high-risk review targets such as ICs, drivers, regulators, connectors, terminals, fuses, and sense resistors
- Cache datasheets from component `Datasheet` fields and extract searchable text
- Build keyword maps for faster datasheet reading
- Review each IC with a pin-by-pin checklist
- Review connectors, motors, loads, supply inputs, sense resistors, and current paths
- Automatically discover and apply baseline, domain-specific, and project-local checklists
- Generate final reports with high-severity findings, warnings, manual-review items, and parser limitations

For example, if a schematic contains the free-text annotation `30W DC-Motor` and the design has a `+24V` rail, the review context preserves that annotation as design-intent evidence. The reviewer can then calculate `30W / 24V = 1.25A` and compare that against connector contact ratings, terminal ratings, sense resistor power, and motor-driver thermal limits.

## What It Checks

- Component fields: Reference, Value, Footprint, Datasheet, MPN, Manufacturer
- IC supply, ground, enable, reset, boot, mode, VREF, ISEN, fault, and exposed-pad pins
- Required datasheet external parts such as decoupling capacitors, bulk capacitors, bootstrap capacitors, charge-pump capacitors, current-sense resistors, pull-ups, TVS/ESD parts, clocks, and feedback networks
- Motor drivers and H-bridges: VM capacitance, current limit, sense resistor power, PowerPAD requirements, and motor output connectors
- DCDC converters: input/output capacitors, inductors, feedback dividers, compensation, BOOT/SW/EN/PGOOD pins
- Connectors and terminals: current, wire gauge, temperature, paralleled contacts, supply path, and return path
- Schematic design intent from text annotations, such as power, voltage, current, `motor`, `heater`, and `load`

## What It Does Not Prove

- It does not replace KiCad ERC.
- It does not replace human datasheet reading.
- It does not claim trace width, thermal vias, copper pours, or EMC are verified when PCB evidence is missing.
- It does not claim ratings are verified when the datasheet is missing or weakly extracted.
- It does not assume stall current, wire gauge, ambient temperature, or fuse behavior unless the user or schematic provides that information.

## Installation

Use Python 3.10+.

```bash
python3 -m venv .venv
. .venv/bin/activate
python -m pip install -r requirements.txt
```

`requirements.txt` currently includes `pypdf` for PDF datasheet text extraction. If `pdftotext` is installed on the system, `datasheet_tool.py` can also use it as a fallback.

## Using It With Codex

Place this folder where Codex can load local skills or plugins, then ask the agent to use `kicad-schematic-review`.

Example prompt:

```text
Use the kicad-schematic-review skill to review this KiCad project.
Focus on motor drivers, connector current ratings, required datasheet external parts,
and sense resistor power.
Project path: /path/to/KiCadProject
```

If you know the design intent, provide it up front:

```text
Input voltage is 24V.
Each motor is 30W. Estimate startup current as 3x nominal.
J1 must be control-signal only; motor power must use a separate terminal.
```

## Command-Line Tools

Inventory a project:

```bash
python scripts/inventory_project.py /path/to/KiCadProject --pretty
```

Extract schematic facts:

```bash
python scripts/extract_kicad_sch.py /path/to/project.kicad_sch --pretty
```

Build compact review context:

```bash
python scripts/build_review_context.py /path/to/KiCadProject --pretty
```

Cache and extract a datasheet:

```bash
python scripts/datasheet_tool.py fetch "https://example.com/part.pdf" --cache-dir /path/to/KiCadProject/datasheet_cache
python scripts/datasheet_tool.py extract /path/to/KiCadProject/datasheet_cache/part.pdf --out /path/to/KiCadProject/datasheet_cache/part.datasheet.txt
python scripts/datasheet_tool.py keywords /path/to/KiCadProject/datasheet_cache/part.datasheet.txt --out /path/to/KiCadProject/datasheet_cache/part.keywords.md
```

`datasheet_tool.py fetch` handles a common supplier-site problem: a URL may look like a `.pdf` but return an HTML wrapper page. The tool attempts to resolve canonical links, PDF links, and supplier-page links to cache the real PDF when possible.

## Review Outputs

Recommended output structure inside the reviewed KiCad project:

```text
KiCadProject/
├── schematic_review.md                 # Final report
├── datasheet_cache/                    # Datasheet PDF/text/keywords/summary files
└── review_outputs/
    ├── extracted/                      # Inventory, extraction, and context JSON
    ├── U2_DRV8870DDA_review.md         # Per-IC instance review
    ├── power_path_review.md            # Supply, connector, and load-path review
    └── ...
```

Final reports should clearly separate:

- `pass`: enough evidence shows the requirement is satisfied
- `fail`: a datasheet, checklist, or rating requirement is clearly violated
- `warning`: risky, incomplete, low-margin, or dependent on unknown system conditions
- `manual_review`: the available project files are not enough to decide

## Repository Layout

```text
SKILL.md                                  Skill workflow and review contract
requirements.txt                          Python dependencies
agents/openai.yaml                        Codex/OpenAI agent metadata
scripts/inventory_project.py              Project file discovery
scripts/extract_kicad_sch.py              Schematic fact extraction
scripts/build_review_context.py           IC/current-path/checklist context builder
scripts/datasheet_tool.py                 Datasheet fetch/extract/keyword helper
references/checklist_example.md           Baseline checklist
references/checklists/motor_driver.md     Motor-driver checklist
references/checklists/connector_power.md  Connector and power-path checklist
references/checklists/dcdc.md             DCDC checklist
references/datasheet_summary_template.md  Datasheet summary template
references/ic_review_template.md          IC instance review template
references/power_path_review_template.md  Power-path review template
references/report_template.md             Final report template
```

## How To Make This Skill More Knowledgeable

The best way to improve this skill is not to put every piece of knowledge into one prompt. Put each kind of knowledge in the layer where it belongs.

### 1. Update `SKILL.md`

Use `SKILL.md` for permanent workflow rules:

- Which scripts must be run
- Which evidence must appear in the final report
- What counts as high severity
- When the reviewer must not say `verified`
- When new domain checklists should be loaded

If the agent should always follow a review principle, put it here.

### 2. Add `references/checklists/*.md`

Use domain checklists for reusable circuit knowledge. Keep one circuit class per file:

```text
references/checklists/
  motor_driver.md
  connector_power.md
  dcdc.md
  usb_c.md
  can.md
  rs485.md
  mcu.md
  ldo.md
```

Then update `scripts/build_review_context.py` so it can automatically load the right checklist based on library IDs, values, net names, and schematic text. This is what turns checklists from static documentation into active review rules.

### 3. Improve `scripts/build_review_context.py`

This is where automatic recognition belongs. Good additions include:

- Parse schematic text such as `30W`, `2A`, `24V`, and `stall current`
- Detect USB-C, CAN, RS485, buck converters, LDOs, MCUs, and load switches from component and net names
- Improve current-critical candidate detection
- Discover project-local checklists
- Generate manual-review questions from missing voltage, current, wire-gauge, or datasheet evidence

This is one of the highest-leverage files for making the skill smarter.

### 4. Improve `scripts/extract_kicad_sch.py`

This is where KiCad fact extraction belongs. Useful improvements include:

- Better hierarchical sheet parsing
- Extract sheet pins, buses, graphical notes, and net classes
- Improve cross-sheet and global-net handling
- Output more raw evidence locations for report citations

### 5. Improve `scripts/datasheet_tool.py`

This is where datasheet acquisition and text extraction belong. Useful improvements include:

- Support more supplier redirect and wrapper-page patterns
- Support local PDF, HTML, TXT, and Markdown sources
- Add better real-PDF resolution for LCSC, TI, ADI, ST, Mouser, and DigiKey pages
- Produce more stable keyword reading maps

### 6. Improve The Templates

Templates shape report quality:

- `references/datasheet_summary_template.md`: make datasheet summaries more pin-centric
- `references/ic_review_template.md`: make per-IC reviews more thorough
- `references/power_path_review_template.md`: make current, wire gauge, derating, temperature, and connector ratings clearer
- `references/report_template.md`: make final reports better for hardware design reviews

### Recommended Growth Path

1. Add `usb_c.md`, `can.md`, `rs485.md`, `ldo.md`, and `mcu.md` checklists.
2. Add auto-trigger rules for those checklists in `build_review_context.py`.
3. Add one or two real KiCad projects as regression examples for each circuit class.
4. Script common high-severity checks, such as missing VM caps, connector current exceeded, and VREF out of range.
5. Make the final report always list datasheets as verified, missing, weakly extracted, or manual-review only.

## License

MIT. See `LICENSE`.
