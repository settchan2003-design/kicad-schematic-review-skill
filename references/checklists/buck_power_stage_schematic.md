# Buck Power Stage Schematic Checklist

Apply this checklist when the schematic contains a nonsynchronous or synchronous buck converter, step-down regulator, external catch diode, adjustable feedback divider, or buck power-stage sizing evidence.

## Net And Pin Logic

- [ ] Buck converter input supply pins must connect to an input voltage range that satisfies the selected regulator datasheet.
- [ ] Buck converter output net must connect to the intended load voltage domain.
- [ ] Adjustable buck feedback pin must connect to the output-voltage divider or datasheet-required feedback network.
- [ ] Enable, power-good, frequency, soft-start, compensation, and mode pins must have defined states or component networks required by the selected regulator datasheet.
- [ ] A nonsynchronous buck converter must include the rectifier diode or freewheel path required by the selected regulator topology.

## Required Topology

- [ ] Buck input must include the minimum input capacitance required by the regulator datasheet.
- [ ] Buck output must include output capacitance that satisfies the regulator datasheet and the computed ripple or transient requirement.
- [ ] The buck inductor must be in series between the switching node and output node for a conventional buck power stage.
- [ ] An adjustable-output buck must include a feedback divider unless the selected regulator uses a different datasheet-specified feedback topology.
- [ ] A nonsynchronous buck must include a rectifier diode whose current and voltage ratings satisfy the computed stresses.
- [ ] An internally compensated buck must use the datasheet-recommended inductor and capacitor values or the datasheet-approved adjustment method.

## Component Parameter Bounds

- [ ] Maximum duty cycle must satisfy $D = V_{OUT} / (V_{IN(max)} \times \eta)$.
- [ ] Inductor ripple current must satisfy $\Delta I_L = (V_{IN(max)} - V_{OUT}) \times D / (f_S \times L)$.
- [ ] Selected regulator maximum output current must satisfy $I_{MAXOUT} = I_{LIM(min)} - \Delta I_L / 2$.
- [ ] Application peak switch current must satisfy $I_{SW(max)} = I_{OUT(max)} + \Delta I_L / 2$.
- [ ] Inductor current rating must be greater than $I_{SW(max)}$.
- [ ] If no datasheet inductor range is given, estimated inductor value must satisfy $L = V_{OUT} \times (V_{IN} - V_{OUT}) / (\Delta I_L \times f_S \times V_{IN})$.
- [ ] Estimated inductor ripple current must satisfy $\Delta I_L = 0.2 \times I_{OUT(max)}$ to $0.4 \times I_{OUT(max)}$ when using the SLVA477B estimation method.
- [ ] Rectifier diode average forward current must satisfy $I_F = I_{OUT(max)} \times (1 - D)$.
- [ ] Rectifier diode power dissipation must satisfy $P_D = I_F \times V_F$.
- [ ] Feedback divider current must satisfy $I_{R1/2} \ge 100 \times I_{FB}$.
- [ ] Feedback lower resistor must satisfy $R_2 = V_{FB} / I_{R1/2}$.
- [ ] Feedback upper resistor must satisfy $R_1 = (V_{OUT} - V_{FB}) / I_{R1/2}$.
- [ ] Minimum output capacitance for ripple must satisfy $C_{OUT(min)} = \Delta I_L / (8 \times f_S \times \Delta V_{OUT})$.
- [ ] Output ripple from capacitor ESR must satisfy $\Delta V_{OUT(ESR)} = ESR \times \Delta I_L$.
- [ ] Minimum output capacitance for load-transient overshoot must satisfy $C_{OUT(min,OS)} = \Delta I_{OUT}^2 \times L / (2 \times V_{OUT} \times V_{OS})$.
- [ ] Input capacitor dielectric must be X5R or better when following the SLVA477B ceramic-capacitor recommendation.
- [ ] Output capacitor dielectric must be X5R or better when following the SLVA477B ceramic-capacitor recommendation.

## Absolute Maximum Ratings

- [ ] Regulator VIN pin voltage must remain inside the selected regulator absolute maximum rating.
- [ ] Switching-node voltage must remain inside the selected regulator absolute maximum rating.
- [ ] Rectifier diode reverse voltage rating must be greater than the maximum switching-node reverse stress from the selected topology.
- [ ] Inductor saturation current rating must be greater than $I_{SW(max)}$.
- [ ] Output capacitor voltage rating must be greater than the maximum output voltage including tolerance and transient overshoot.
- [ ] Input capacitor voltage rating must be greater than the maximum input voltage including tolerance and transient overshoot.

## Source Notes

- Distilled from TI SLVA477B buck converter power-stage calculation guidance.
