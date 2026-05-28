# DCDC Checklist

Apply this checklist when the schematic contains a switching regulator, buck, boost, flyback, charge pump, or DC/DC converter.

## Required External Parts

- Input capacitors must match datasheet value, voltage rating, ripple current, and placement guidance.
- Output capacitors must match datasheet value, ESR/stability range, voltage rating, and ripple current.
- Inductor value, saturation current, RMS current, DCR, and package must be checked against load current and switching current.
- Bootstrap, charge-pump, compensation, soft-start, bias, and internal-regulator capacitors must be present when required.
- Feedback divider values must produce the intended output voltage using the datasheet equation.

## Pins And States

- EN/UVLO, PGOOD, MODE/SYNC, RT/FSW, SS/TRK, BOOT/SW, FB, COMP, and exposed pad pins must have intentional connections.
- Absolute maximum and recommended operating voltage ranges must be checked for VIN, SW, BOOT, EN, FB, and bias pins.
- Unused pins must follow datasheet guidance.

## Layout And Ratings

- Hot loop, switch node, input capacitor return, diode/FET path, and sense/feedback routing must be flagged for PCB review.
- Power components must be rated for worst-case voltage, current, ripple, temperature, and derating.
- If PCB layout is missing, layout-sensitive claims remain `manual_review`.
