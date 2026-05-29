# Power Entry, Inrush, And Precharge Checklist

Apply this checklist when the schematic contains a battery input, DC bus, relay, solid-state relay, hot-swap switch, ideal diode, precharge path, large downstream bulk capacitance, motor controller bus, or text/net names implying high power entry.

## Input Definition And Ratings

- Power entry must state nominal voltage, maximum voltage, reverse-polarity behavior, expected continuous current, and expected peak/inrush current.
- Connectors, fuses, switches, relays, MOSFETs, shunts, and current-sense parts must be rated for continuous current, pulse current, voltage, temperature, and fault interruption where applicable.
- Supply and return paths must have comparable current capacity; do not verify only the positive-side path.
- Input capacitors must have voltage rating, ripple-current rating, surge tolerance, and temperature derating appropriate for the bus.

## Inrush And Precharge

- If large downstream capacitors or multiple motor controllers are present, estimate worst-case inrush from bus voltage, initial capacitor voltage, capacitance, source impedance, and any series resistance.
- A precharge, soft-start, hot-swap, NTC, current-limited switch, or staged-enable strategy should be present when inrush can exceed connector, relay, MOSFET, fuse, or battery limits.
- Precharge resistors must be checked for pulse energy, average power during repeated startup, voltage rating, and bypass timing.
- Bleed/discharge resistors must be checked for steady-state dissipation, voltage rating, discharge time, and user-accessible residual voltage assumptions.
- Bypass MOSFETs/relays must not close until downstream capacitance is sufficiently charged; the control circuit should fail safe if timing or sensing fails.
- Discharge paths and residual bus voltage behavior should be documented when large capacitors remain charged after power-off.

## MOSFET Or Solid-State Relay Paths

- Parallel MOSFET paths require current-sharing rationale, matched layout, thermal coupling assumptions, and per-device current/thermal calculations.
- Gate-drive voltage, gate-source protection, pulldowns, turn-on speed, and source/drain orientation must be checked for the actual high-side or low-side topology.
- Load disconnect must consider inductive kick, regenerative current, reverse current, and body-diode conduction paths.
- If the switching element sees a capacitive load, distinguish steady-state current from charging surge current in the finding.

## Bring-Up And Test Expectations

- Bring-up should include no-load and loaded rail checks, input/output ripple, switch-node waveform, short-circuit/overcurrent behavior, and thermal observation under realistic load.
- If expected bus capacitance, cable length, battery/internal resistance, or load profile is unknown, report inrush margin as `manual_review`.

## Source Notes

- Enriched from the hardware onboarding manual sections on robot power entry, solid-state relay failures, large input capacitors, and precharge/current limiting.
