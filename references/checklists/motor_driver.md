# Motor Driver Checklist

Apply this checklist when the schematic contains a motor driver, H-bridge, gate driver used for a motor/load, motor connector, or text/net names implying a motor.

## Supply And Energy

- Each motor-driver VM/VBB/VBAT supply pin must have datasheet-required local ceramic bypass capacitance.
- Each motor-driver supply rail should have local bulk capacitance sized for startup, braking, and cable/load transients.
- The bulk capacitor voltage rating should exceed the worst-case supply voltage with margin.
- Motor supply entry connectors, fuses, switches, and traces must be rated for continuous and startup/stall current.
- If motor power is annotated in the schematic, compute nominal current from `I = P / V` and use it in the power-path review.

## Outputs And Protection

- Motor outputs must route directly to the intended motor connector/load pins with polarity documented.
- Output connector current, voltage, wire gauge, and temperature ratings must be checked against continuous and startup/stall current.
- Inductive-load protection, snubbers, TVS, or EMI parts should be considered when cable length or motor environment is unknown.
- High-current output nets must be called out for later PCB trace-width and copper-area review.

## Control And Current Limit

- Input pins must have defined controller voltage domains and safe startup/reset states.
- Enable, sleep, mode, brake/coast, and fault pins must have intentional states.
- Current-sense resistors must include value, package, power rating, tolerance, and pulse capability.
- Current-limit equations from the datasheet must be evaluated using schematic resistor values and reference voltages.
- Sense traces should be reviewed for Kelvin routing when current accuracy matters.

## Thermal And Layout

- Exposed pads and thermal pins must connect as the datasheet requires.
- PCB review must check driver copper area, thermal vias, high-current loops, and separation from sensitive inputs.
- If PCB layout is missing or empty, thermal and high-current layout items remain `manual_review`.
