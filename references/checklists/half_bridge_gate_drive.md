# Half-Bridge And Gate-Drive Checklist

Apply this checklist when the schematic contains a half bridge, H-bridge, external MOSFET/IGBT/SiC stage, gate driver, bootstrap high-side driver, inverter phase leg, or text/net names implying `GH`, `GL`, `HO`, `LO`, `HB`, `HS`, `SW`, `PHASE`, `U/V/W`, or `SiC`.

## Gate Drive Supply And Bootstrap

- Gate-driver supply voltage must be compatible with the MOSFET/IGBT gate rating and the required on-state gate voltage.
- Bootstrap capacitor value, voltage rating, and local placement must follow the driver datasheet; bootstrap diode reverse voltage must cover the bus voltage plus transients.
- High-side driver common/switch pins must connect to the correct source/switch node, not quiet ground.
- Isolated drivers must show isolated power, isolated return, creepage/clearance intent, and any required primary/secondary decoupling.
- Gate-driver UVLO thresholds must be compatible with safe MOSFET turn-on and turn-off behavior.

## Gate Loop And Switching Control

- Gate resistors must be present or intentionally omitted; separate turn-on/turn-off paths should be considered when switching speed, ringing, or shoot-through margin matters.
- Gate-to-source pulldown resistors should define the off state during reset, driver high impedance, connector unplug, or MCU boot.
- Miller clamp, negative turn-off bias, or other crosstalk suppression should be considered for fast half bridges, SiC MOSFETs, high bus voltage, or high dv/dt operation.
- Dead time, interlock, and shoot-through prevention must be explicit in the driver, controller, or firmware assumptions.
- MOSFET VGS absolute maximum, negative VGS limit, threshold voltage, total gate charge, and driver peak current must be checked against the selected driver and gate network.

## Crosstalk And Parasitics

- For SiC or fast-switching half bridges, treat crosstalk as a first-class review item: off-state gate voltage can be driven by gate-drain capacitance, common-source inductance, and gate-loop impedance.
- Positive off-state gate spikes must remain below the effective turn-on threshold with margin; negative spikes must remain within the MOSFET allowed negative VGS limit.
- Common-source inductance should be minimized by Kelvin-source packages, Kelvin driver returns, tight gate loops, and careful source-current separation where layout evidence exists.
- If only schematic evidence is available, report crosstalk, ringing, gate-loop inductance, and Kelvin-source implementation as `manual_review`.

## Power Stage Protection

- Drain-source voltage rating must cover bus voltage, ringing, load dump/regeneration, and fault transients.
- Current rating, SOA/pulse capability, RDS(on), package thermal resistance, and heatsinking/copper assumptions must match continuous and peak load current.
- Phase-node snubbers, TVS/clamps, RC damping, or gate-speed limits should be considered when cable length, motor inductance, or switching ringing is unknown.
- Body diode or reverse-recovery behavior must be checked for synchronous rectification, dead time, and regenerative current paths.

## Source Notes

- Enriched from the SiC MOSFET half-bridge crosstalk modeling paper and the hardware onboarding manual gate-drive sections.
