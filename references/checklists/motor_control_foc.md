# Motor Control And FOC Checklist

Apply this checklist when the design uses BLDC/PMSM/ACIM FOC, SVPWM, three-phase inverter control, encoder/resolver/Hall feedback, phase-current sampling, or firmware notes implying motor current/velocity/position loops.

## Power Stage And Feedback Topology

- Record motor type, bus voltage, expected phase current, peak/stall current, PWM frequency, control-loop rate, and modulation strategy.
- Three-phase inverter outputs must map unambiguously to motor phases; phase order and polarity should have a bring-up/calibration plan.
- Phase-current sensing topology must match the FOC algorithm assumptions: single-shunt, dual-shunt, three-shunt, inline, or sensorless estimator.
- DC-bus voltage sensing must map the maximum bus and regeneration/overvoltage cases into the ADC range with margin.
- Encoder, resolver, Hall, or sensorless feedback paths must specify voltage domain, pull-ups, filtering, connector pinout, shielding/grounding, and fault behavior.

## Sampling And Timing

- PWM timer, ADC trigger timing, current-sampling windows, dead time, and blanking/filter delays must be compatible.
- Dead time should be documented and reviewed for both shoot-through prevention and low-speed current distortion.
- Current-loop bandwidth, sampling frequency, and sensor/filter delay should be compatible with the motor electrical time constant and desired torque response.
- Offset calibration and current zeroing must occur at a safe state where phase current is known or controlled.
- Firmware watchdogs or command timeouts should put the inverter into a safe state if communication or control updates stop.

## Protection And Limits

- Hardware overcurrent, overvoltage, undervoltage, overtemperature, and desaturation/VDS monitoring should be independent enough to protect the power stage if firmware misbehaves.
- Regeneration/braking energy must have a path: bus capacitance, brake chopper, supply absorption, or explicit overvoltage shutdown.
- Gate-driver fault outputs, motor-driver diagnostics, and thermal warnings should be connected to the controller or latched/protected locally.
- Motor connector, phase wiring, and current sensors must be rated for continuous and peak phase current, temperature rise, and vibration/cable strain.

## Calibration And Bring-Up

- Bring-up should include phase-order check, encoder electrical-angle offset, current-sense gain/offset calibration, bus-voltage calibration, and low-current open-loop test before closed-loop torque.
- Direction conventions for phase currents, encoder angle, PWM polarity, and torque command should be documented to avoid sign errors.
- Sensorless startup or low-speed operation requires an explicit startup/forced-angle/open-loop strategy and safe fallback on failed lock.
- If only schematic evidence exists, firmware parameters, current-loop stability, phase-order calibration, and encoder linearity remain `manual_review`.

## Source Notes

- Enriched from FOC control notes, TI FOC material, and motor-driver design reports.
