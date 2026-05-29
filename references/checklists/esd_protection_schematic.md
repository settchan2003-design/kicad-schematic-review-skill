# ESD Protection Schematic Checklist

Apply this checklist when the schematic contains external connectors, user-accessible signals, USB, HDMI, Ethernet, CAN, LIN, RS-232, RS-485, RF, antenna, button, keypad, display, SIM, SD card, battery, charger, or other exposed interfaces.

## Net And Pin Logic

- [ ] Every externally accessible signal net must have an explicit ESD protection decision: protected by a listed ESD suppressor, protected by the connected IC's documented ESD rating, or marked `manual_review`.
- [ ] A unidirectional TVS/diode-array device must have its cathode/anode orientation compatible with the protected signal polarity and reference rail.
- [ ] A bidirectional ESD suppressor must be used when the protected signal swings both positive and negative with respect to the reference node.
- [ ] Multi-line ESD arrays must map each protected channel to the intended signal net and reference pin.
- [ ] ESD device reference pins must connect to the intended reference node required by the device datasheet.

## Required Topology

- [ ] Protected single-ended signal nets must include one ESD current path from the protected net to a valid reference node or rail-clamp network.
- [ ] Protected differential or multi-wire interfaces must protect every exposed conductor in the interface group.
- [ ] Rail-clamp ESD arrays must include valid connections to the rail pins required by the ESD-array datasheet.
- [ ] Power-entry and charger-input nets exposed to users must include a surge/ESD suppressor whose working voltage exceeds the maximum normal operating voltage.

## Component Parameter Bounds

- [ ] ESD suppressor reverse working voltage must be greater than or equal to the maximum normal signal voltage: $V_{RWM} \ge V_{SIGNAL(MAX)}$.
- [ ] ESD suppressor clamping voltage must be less than the protected IC pin's survivable transient voltage: $V_{CLAMP(MAX)} < V_{PIN(SURGE\_MAX)}$.
- [ ] ESD suppressor line capacitance must be less than or equal to the interface capacitance budget: $C_{ESD} \le C_{INTERFACE(MAX)}$.
- [ ] ESD suppressor surge current rating must be greater than or equal to the required surge current for the selected IEC or system test level.
- [ ] ESD suppressor channel count must be greater than or equal to the number of exposed conductors being protected.

## Absolute Maximum Ratings

- [ ] The protected IC normal pin voltage range must not exceed the ESD suppressor working-voltage range.
- [ ] The ESD suppressor leakage at maximum operating voltage must be less than the protected node leakage budget.
- [ ] The selected ESD suppressor IEC 61000-4-2 contact-discharge rating must be greater than or equal to the required contact-discharge test level.
- [ ] The selected ESD suppressor IEC 61000-4-2 air-discharge rating must be greater than or equal to the required air-discharge test level.

## Source Notes

- Distilled from Littelfuse ESD suppression design guidance.
