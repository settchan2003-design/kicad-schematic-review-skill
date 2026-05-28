# Datasheet Summary

Purpose: capture what the IC datasheet requires or recommends. This file is the design contract used later by the IC review. Do not judge the schematic here except when noting what must be checked.

## Identity

- Part:
- Manufacturer:
- Package:
- Source datasheet link/path:
- Source pages/sections used:
- Summary status: draft / verified / needs-human-check

## Pin-Level Requirements

Create one row per physical pin in the reviewed package. If the datasheet groups pins, still expand them here so the schematic review can compare pin by pin.

| Pin | Name | Type | Function | Required/Allowed Connection | Required External Parts | Recommended Values/Ratings | Layout/Placement Notes | If Unused | Evidence |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |

## Pin Detail Notes

Use this section for pins whose requirements do not fit cleanly in the table.

### Pin <number> - <name>

- Function:
- Must connect to:
- May connect to:
- Must not connect to:
- Required external components:
- Recommended component values:
- Placement/layout constraints:
- Startup/reset/sequence constraints:
- Unused-pin rule:
- Datasheet evidence:

## Power And Energy Storage Requirements

- Supply pins:
- Allowed voltage range:
- Recommended operating conditions:
- Absolute maximum notes:
- Per-pin decoupling:
- Bulk/input capacitance:
- Output/load capacitance:
- Bootstrap/charge-pump capacitance:
- Reservoir/motor-bus capacitance:
- Current rating notes:
- Power sequencing:

## Connector / Power Path Ratings

Use this section for connectors, terminals, fuses, switches, cables, current-sense resistors, and any current-carrying component.

- Current rating:
- Voltage rating:
- Applicable wire gauge or mating part:
- Contact resistance:
- Temperature range:
- Derating notes:
- Number of contacts carrying current:
- Parallel-contact assumptions, if any:
- Evidence:

## Protection And Reliability Requirements

- Reverse polarity:
- Overcurrent / current sense:
- Flyback / recirculation path:
- TVS / ESD:
- Thermal pad / exposed pad:
- Fault pins:
- Diagnostic pins:

## Configuration Pins

- Reset / enable:
- Boot / mode / strap:
- Address selection:
- Current limit / gain / slew-rate setting:
- Unused pin handling:

## Clock And Timing

- Internal/external clock options:
- Crystal/resonator requirements:
- Special timing constraints:

## Interfaces

- Digital interfaces:
- Analog interfaces:
- Differential/high-speed interfaces:
- Motor/inductor/load drive pins:
- Voltage domain constraints:
- Pull-up/pull-down requirements:

## Typical Application Circuit Requirements

Convert every relevant datasheet application-circuit item into a checkable row.

| Requirement ID | Related Pins | Required/Recommended Component | Recommended Value/Rating | Hard Requirement or Recommendation | Evidence |
| --- | --- | --- | --- | --- | --- |

## Cross-Pin Requirements

Use this for requirements involving multiple pins or the whole IC.

| Requirement ID | Related Pins/Nets | Requirement | Expected Schematic Evidence | Result If Missing |
| --- | --- | --- | --- | --- |

## Package And Variant Caveats

- Package-specific pinout differences:
- Variant-specific feature differences:
- Pins whose names/functions change by mode:

## Review Rules For This IC

- Check every schematic pin against `Pin-Level Requirements`.
- Verify every required external component exists and has plausible value/rating.
- Treat recommended values as warnings when absent or very different unless the design gives a reason.
- Separate absolute requirements from typical-application recommendations.
- For connectors and power-path components, compare expected continuous/peak current against datasheet current rating and flag missing derating margin.

## Open Questions

- 
