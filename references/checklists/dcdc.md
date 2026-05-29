# DCDC Checklist

Apply this checklist when the schematic contains a switching regulator, buck, boost, flyback, charge pump, or DC/DC converter.

## Required External Parts

- Input capacitors must match datasheet value, voltage rating, ripple current, and placement guidance.
- Output capacitors must match datasheet value, ESR/stability range, voltage rating, and ripple current.
- Inductor value, saturation current, RMS current, DCR, and package must be checked against load current and switching current.
- Inductor saturation current should be checked against the regulator current-limit or peak switch current, not only nominal load current; include short-circuit behavior when the datasheet exposes it.
- Bootstrap, charge-pump, compensation, soft-start, bias, and internal-regulator capacitors must be present when required.
- Feedback divider values must produce the intended output voltage using the datasheet equation.
- For constant-on-time, hysteretic, or ripple-injection regulators, verify that the FB ripple generation method is intentional and matches the datasheet or application note. All-ceramic output capacitors can remove the ESR ripple needed for stable operation unless a Type III/ramp-injection or equivalent network is provided.
- For Fly-Buck or coupled-inductor topologies, verify transformer/coupled-inductor turns ratio, isolation rating, rectifier voltage rating, primary and secondary output capacitors, Type III ripple requirement when specified, and secondary load regulation assumptions.
- Soft-start, compensation, feed-forward, and frequency-setting parts should be checked against startup overshoot, transient load response, and switching-frequency expectations.

## Pins And States

- EN/UVLO, PGOOD, MODE/SYNC, RT/FSW, SS/TRK, BOOT/SW, FB, COMP, and exposed pad pins must have intentional connections.
- Absolute maximum and recommended operating voltage ranges must be checked for VIN, SW, BOOT, EN, FB, and bias pins.
- Unused pins must follow datasheet guidance.
- UVLO divider values and hysteresis must match the expected input range and brownout behavior. If UVLO is tied directly to VIN, state the implied startup threshold.
- Internal regulator pins such as VCC must have the required bypass capacitor and must not be overloaded by external circuitry unless the datasheet permits it.

## Layout And Ratings

- Hot loop, switch node, input capacitor return, diode/FET path, and sense/feedback routing must be flagged for PCB review.
- Power components must be rated for worst-case voltage, current, ripple, temperature, and derating.
- The high-frequency input bypass capacitor should be directly across VIN and return pins with minimal loop area; if the bulk capacitor is remote, require a small local ceramic bypass near the IC.
- VCC, bootstrap, and charge-pump capacitors should be close to their IC pins with short, low-loop connections.
- Feedback traces should be routed away from inductors, transformers, switch nodes, and other fast switching traces; if PCB evidence is unavailable, keep this as `manual_review`.
- Switch-node copper should be only as large as needed and must not be tied to unnecessary planes or pours.
- The inductor should be close to the SW pin, but the SW copper should balance current capacity against EMI and parasitic capacitance; do not enlarge it into unrelated copper.
- Input-capacitor ground, output-capacitor ground, power ground, and exposed pad/thermal ground should form a short low-impedance power return where the datasheet layout shows it.
- Thermal vias and solid copper should be reviewed for regulator ICs, power diodes/FETs, and hot inductors; thermal-relief spokes can be inappropriate for high-current/thermal paths.
- For long input leads plus low-ESR ceramic input capacitors, check for damping or bulk capacitance that prevents VIN overshoot and input-filter instability.
- If PCB layout is missing, layout-sensitive claims remain `manual_review`.

## Source Notes

- Enriched from TI LM5017 datasheet layout/ripple guidance and TI AN-1481/SNVA166A COT ripple-generation guidance.
