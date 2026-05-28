# Connector And Power Path Checklist

Apply this checklist when a connector, terminal block, fuse, switch, cable, supply rail, battery, motor, heater, actuator, or other load-current path is present.

## Ratings

- Every current-carrying connector or terminal must have a datasheet or supplier rating source.
- Compare current per contact against continuous current, startup/stall/peak current, ambient temperature, and wire gauge.
- Flag warning when expected continuous current exceeds 70% of the contact rating unless a project checklist gives a different derating rule.
- Flag fail when expected continuous current exceeds the contact rating.
- Verify voltage rating against the maximum possible rail voltage, not only the nominal label.
- If contacts are paralleled, require explicit cable/harness evidence and current-sharing rationale.

## Power Entry

- Power entry must show polarity, expected voltage, return path, and protection strategy.
- Supply and return contacts should have matched current capacity.
- Fuses, switches, shunts, and protection parts must have current, voltage, power, and interrupt ratings where applicable.
- Connector footprints must match the exact series/pitch/current class assumed by the datasheet.

## Evidence Gaps

- If datasheet fetch returns an HTML wrapper or supplier page, resolve the actual PDF/drawing before calling ratings verified.
- If current is unknown, ask for continuous and peak/stall current and still report unknown rating margin as `manual_review`.
- If PCB layout is missing, mark trace width, copper weight, thermal rise, and creepage/clearance as `manual_review`.
