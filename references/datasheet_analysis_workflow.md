# Datasheet Analysis Workflow

Use this when creating `datasheet_cache/<part>.summary.md`.

## Steps

1. Resolve the datasheet source from the component `Datasheet` property.
2. Cache the datasheet with `scripts/datasheet_tool.py fetch`.
3. Extract text with `scripts/datasheet_tool.py extract`.
4. Create a keyword map with `scripts/datasheet_tool.py keywords`.
5. Read only the sections needed to fill `datasheet_summary_template.md`.
6. Write a pin-centric summary.

## What To Capture

- Exact package/variant being reviewed.
- Pin table and pin descriptions.
- Absolute maximum and recommended operating conditions.
- Typical application circuit.
- Required and recommended external parts.
- Layout recommendations.
- Thermal and exposed pad rules.
- Unused pin rules.
- Mode, strap, reset, enable, address, current-limit, and fault behavior.

## Evidence Rules

- Cite page, section, table, or figure names when available.
- Keep evidence concise.
- If the datasheet text extractor is noisy, mark uncertain fields as `manual_review`.
- Do not convert example-only values into hard failures unless the datasheet says they are required.
