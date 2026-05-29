# Motor Driver Checklist

Apply this checklist when the schematic contains a motor driver, H-bridge, gate driver used for a motor/load, motor connector, or text/net names implying a motor.

## Supply And Energy

- Each motor-driver VM/VBB/VBAT supply pin must have datasheet-required local ceramic bypass capacitance.
- Each motor-driver supply rail should have local bulk capacitance sized for startup, braking, and cable/load transients.
- The bulk capacitor voltage rating should exceed the worst-case supply voltage with margin.
- Bulk capacitors should be near the board power entry or motor driver supply path, use low ESR where appropriate, and connect to power/ground planes with enough vias for current.
- Small high-frequency bypass capacitors should be closest to the driver or power stage pins; larger capacitors should follow after the smaller local capacitors.
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
- Use the actual resistor datasheet when available. As a rough default only, common chip-resistor package power ratings are: 0201 1/20 W, 0402 1/16 W, 0603 1/10 W, 0805 1/8 W, 1206 1/4 W, 1210 1/3 W, 1812 1/2 W, 2010 3/4 W, 2512 1 W.
- Current-limit equations from the datasheet must be evaluated using schematic resistor values and reference voltages.
- Sense traces should be reviewed for Kelvin routing when current accuracy matters.
- For FOC/current-loop designs, current-sense topology and ADC sampling timing should be reviewed with `current_sensing.md` and `motor_control_foc.md`.
- For integrated current-sense amplifiers, check required filtering/decoupling on SPx/SNx or equivalent sense pins and preserve differential symmetry where the datasheet expects it.
- Fault, overcurrent, thermal-warning, and diagnostic outputs should connect to the controller or have a documented reason for being unused.

## Thermal And Layout

- Exposed pads and thermal pins must connect as the datasheet requires.
- PCB review must check driver copper area, thermal vias, high-current loops, and separation from sensitive inputs.
- A continuous low-impedance ground return is preferred; analog, digital, and power regions may be partitioned, but should not create broken return paths or accidental ground-plane slots.
- High-current motor/output loops, bootstrap circuits, charge pumps, switch nodes, and power-stage FETs should be routed away from sensitive analog and digital signals.
- Gate-drive traces should be short and wide; high-side gate traces should run close to their switch-node/source return path to minimize loop area.
- Avoid routing high-frequency bypass current through vias between the bypass capacitor and active device when same-layer placement is feasible.
- PCB review should look for right-angle bends, narrow current bottlenecks, excessive via gaps that split ground return, and insufficient vias for bulk capacitors or high-current paths.
- If PCB layout is missing or empty, thermal and high-current layout items remain `manual_review`.

## Source Notes

- Enriched from TI motor-driver board-layout best practices and the hardware onboarding manual motor-driver sections.
