# Schematic Rule Extraction Template

Use this template when converting a datasheet or application note into a hard schematic-review checklist.

## Guardrails

- Do not include PCB, placement, routing, copper, via, thermal-spreading, length-matching, or geometry guidance.
- Do not use vague wording such as "appropriate", "reasonable", "as needed", "pay attention to", or "consider".
- Every item must be checkable from schematic data, component values, component ratings, datasheet limits, or stated system requirements.
- Use checkbox items only.
- Use formulas when the source document gives formulas.

## Net And Pin Logic

- [ ] `<pin/net>` must connect to `<required state/net/component>`.
- [ ] `<pin/net>` must not be left floating.
- [ ] `<mode/configuration>` requires `<pin/net>` to be `<logic level or voltage range>`.
- [ ] Unused `<pin type>` must be connected to `<required default handling>`.

## Required Topology

- [ ] `<interface/power function>` must include `<required component/network>`.
- [ ] `<protection function>` must connect between `<protected node>` and `<reference node or rail>`.
- [ ] `<matching/termination/bias network>` must include `<component values and endpoints>`.
- [ ] `<power function>` must include `<input/output/storage/bypass network>` with `<required value/rating>`.

## Component Parameter Bounds

- [ ] `<component>` value must satisfy `$<formula>$`.
- [ ] `<component>` value must be within `<min>` and `<max>`.
- [ ] `<component>` rating must be greater than or equal to `<computed stress>`.
- [ ] `<component>` tolerance or ratio must satisfy `<numeric requirement>`.

## Absolute Maximum Ratings

- [ ] `<supply pin>` voltage must remain within `<min>` and `<max>`.
- [ ] `<signal pin>` voltage must remain within `<min>` and `<max>`.
- [ ] `<current path>` current must remain below `<limit>`.
- [ ] `<protection component>` working voltage, clamping voltage, capacitance, and surge rating must satisfy the protected IC/interface limits.
