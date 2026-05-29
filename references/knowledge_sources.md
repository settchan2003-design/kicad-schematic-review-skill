# Knowledge Source Map

This file records which design-document themes have been distilled into reusable review checklists. It intentionally stores no source PDFs or long copied passages.

## Integrated Source Themes

| Source Theme | Distilled Into | Review Focus |
| --- | --- | --- |
| DCDC design fundamentals, MP4560 design notes, Buck PCB layout, DCDC test reports | `checklists/dcdc.md`, `checklists/dcdc_bringup_test.md` | Inductor/capacitor sizing, current limit, hot-loop layout, FB/SW/BST/VCC placement, ripple, efficiency, transient, short-circuit, thermal, and probing checks |
| TI motor-driver layout, MIT motor-driver design, FOC notes, TI FOC material | `checklists/motor_driver.md`, `checklists/motor_control_foc.md`, `checklists/half_bridge_gate_drive.md` | Motor supply energy, gate-drive routing, phase-current feedback, dead time, phase order, encoder/sensor calibration, protection, and safe bring-up |
| High-side/low-side current monitoring, simplified current-sense design, phase-current notes | `checklists/current_sensing.md`, `checklists/mcu_adc.md`, `checklists/motor_driver.md` | Shunt value/power, common-mode range, PWM rejection, ADC range, sampling windows, Kelvin routing, and current-loop signal quality |
| ADC performance and signal sampling/reconstruction notes | `checklists/mcu_adc.md`, `checklists/signal_power_integrity.md` | SAR ADC settling, source impedance, RC filter selection, anti-aliasing, channel sequencing, and measurement fidelity |
| NexFET ringing, gate-resistor design, SiC half-bridge crosstalk | `checklists/half_bridge_gate_drive.md`, `checklists/signal_power_integrity.md` | Gate resistance, switching loss versus damping, common-source inductance, Miller/crosstalk, VGS/VDS stress, snubbers, and probing artifacts |
| Signal and power integrity material plus project test reports | `checklists/signal_power_integrity.md`, `checklists/dcdc_bringup_test.md` | Return paths, termination, differential interfaces, decoupling, PDN assumptions, interface probing, clock quality, and bring-up evidence |
| Littelfuse ESD guide, TI SLLA272D, TI SLVA689, TI SLVA477B | `schematic_rule_extraction_template.md`, `checklists/esd_protection_schematic.md`, `checklists/rs485_schematic.md`, `checklists/i2c_pullup_schematic.md`, `checklists/buck_power_stage_schematic.md` | Layout-free schematic rules for ESD/TVS selection, RS-485 termination/failsafe/loading, I2C pull-up bounds, and buck power-stage formulas |

## Maintenance Rule

When adding more documents, place stable review knowledge into the narrowest applicable checklist and add or tighten `build_review_context.py` trigger rules. Do not paste whole source excerpts into the skill.
