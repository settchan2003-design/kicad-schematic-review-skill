# Current Sensing Checklist

Apply this checklist when the schematic contains shunt resistors, current-sense amplifiers, Hall/current sensors, phase-current feedback, high-side/low-side current monitoring, overcurrent comparators, or net names implying `ISEN`, `CS`, `CSA`, `SHUNT`, `SPx/SNx`, `IPROPI`, or motor phase current.

## Measurement Topology

- Identify whether the design uses high-side, low-side, inline phase, single-shunt, dual-shunt, three-shunt, isolated, Hall, or magnetic current sensing; do not mix their assumptions.
- The sensing location must match the protection/control goal: supply current, phase current, inductor current, solenoid current, or fault-only overcurrent detection.
- High-side and phase-current sensing must check amplifier common-mode range, PWM/common-mode transient rejection, input survival during switching, and supply/headroom over the full bus range.
- Low-side sensing must account for ground lift, return-path voltage drop, and whether the load/controller can tolerate the shunt in the return path.
- Single-shunt or two-shunt motor-current sensing must have valid PWM/ADC sampling windows over the expected modulation range.

## Shunt And Front-End Ratings

- Shunt value must produce enough signal at minimum current without exceeding ADC/amplifier input range at peak or fault current.
- Shunt package, temperature coefficient, tolerance, continuous power, pulse energy, and Kelvin-terminal availability must match the current profile.
- Calculate shunt dissipation with both `I_RMS^2 * R` and relevant pulse/fault energy; do not use only nominal current.
- Sense input filters must preserve differential symmetry and must not create excessive delay for overcurrent protection or current-loop control.
- Comparator thresholds, blanking/filter times, and fault latch/reset behavior must match the power-stage safe operating area.

## ADC And Signal Chain

- Current-sense gain and offset must map expected bidirectional or unidirectional current into the ADC input range with margin.
- The sensor/amplifier reference and ADC reference relationship must be explicit; ratiometric and absolute-reference designs should be reviewed differently.
- Differential-to-single-ended conversion, output common-mode voltage, and ADC input range must be checked when isolated or fully differential sensors are used.
- ADC sampling time, input RC filter, source impedance, and channel sequencing must allow the sample capacitor to settle to the required accuracy.
- Calibration or offset removal should be planned for precision current loops, low-current measurement, and bidirectional sensing.

## Layout And Noise

- Shunt sense lines should use Kelvin routing directly from the shunt terminals to the amplifier input pins.
- Sense traces should avoid switch nodes, gate-drive traces, motor phases, bootstrap nodes, and high-current copper; if PCB evidence is missing, keep these items as `manual_review`.
- Common-mode and differential input filtering should be located at the amplifier pins unless the datasheet recommends otherwise.
- For high dv/dt motor or solenoid systems, require PWM-rejection/current-sense amplifier suitability or document why a slower/filtered measurement is acceptable.

## Source Notes

- Enriched from TI current-sense application material, high-side/low-side motor current monitoring notes, and ADC sampling guidance.
