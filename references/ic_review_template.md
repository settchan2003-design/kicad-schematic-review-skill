# IC Review

Purpose: compare one schematic IC instance against its datasheet summary. The datasheet summary says what should exist; this review records what the schematic actually does and whether it matches.

## Identity

- Reference:
- Part:
- Schematic file:
- Datasheet summary:
- Review status:
- Raw schematic spot-check status:
- Confidence limits:

## Extracted Pin Map

Record the extracted schematic facts before making judgements. If a critical pin looks suspicious, verify it in the raw `.kicad_sch` and note the result.

| Pin | Name | Type | Extracted Net | Connected Components On Net | Raw Spot-Check | Notes |
| --- | --- | --- | --- | --- | --- | --- |

## Per-Pin Connection Review

Create one row per physical pin in the schematic symbol/package. Use the datasheet summary as the expected side and the extracted schematic facts as the actual side.

| Pin | Name | Expected From Datasheet | Actual Schematic Connection | External Parts Found | Result | Confidence | Finding / Evidence | Recommendation |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |

## Detailed Pin Reviews

### Pin <number> - <name>

- Expected from datasheet:
- Actual schematic net:
- Actual connected components:
- Required external parts present:
- Value/rating check:
- PCB/layout dependency, if the datasheet makes one:
- Result:
- Confidence:
- Finding:
- Recommendation:

## Required External Components Review

This section is for parts required by pins or typical application circuits, such as bootstrap capacitors, charge-pump capacitors, motor-bus bulk capacitors, current-sense resistors, pull-ups, snubbers, TVS diodes, or decoupling capacitors.

| Requirement Source | Required Component | Recommended Value/Rating | Actual Component/Value | Result | Confidence | Notes |
| --- | --- | --- | --- | --- | --- | --- |

## Cross-Pin Requirement Review

| Requirement ID | Related Pins/Nets | Expected | Actual | Result | Confidence | Recommendation |
| --- | --- | --- | --- | --- | --- | --- |

## Connection Findings Summary

| Severity | Confidence | Pin/Net | Finding | Evidence | Recommendation |
| --- | --- | --- | --- | --- | --- |

## Voltage And Rating Checks

| Pin/Net | Datasheet Limit/Recommendation | Schematic Value/Net | Result | Notes |
| --- | --- | --- | --- | --- |

## Checklist Results

| Item | Result | Evidence | Notes |
| --- | --- | --- | --- |

## Assumptions

- 

## Manual Review Needed

- 
