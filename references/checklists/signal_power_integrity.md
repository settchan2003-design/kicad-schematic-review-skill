# Signal And Power Integrity Checklist

Apply this checklist when the schematic or notes imply high-speed digital links, differential pairs, clocks, CAN/RS485/USB/Ethernet, fast PWM edges, long cables, dense power distribution, or SI/PI-sensitive measurement/debug requirements.

## Interfaces And Transmission Paths

- Identify each high-speed or noise-sensitive interface, its expected data rate, voltage domain, connector/cable length, and termination requirement.
- Differential interfaces must preserve polarity, common-mode range, bias/failsafe network, termination value/location, and ESD protection strategy.
- Single-ended fast signals should have clear source/load, return path, edge-rate control, and series damping/termination when trace length or ringing risk is material.
- Clocks, crystals, oscillators, and time-critical PWM/ADC trigger signals should be routed and reviewed as noise-sensitive nets.
- External connectors should include ESD, surge, common-mode choke, isolation, or filtering when the environment or cable length requires it.

## Return Paths And Planes

- Every fast signal must have a nearby continuous return path; avoid routing over plane splits, slots, voids, or poorly stitched layer transitions.
- Ground/power plane stitching and decoupling should support return-current continuity when signals change layers.
- Partitioning analog, digital, and power regions must not create broken return paths or shared-impedance coupling into sensitive references.
- High-current loops, motor phases, switch nodes, and gate-drive loops should be physically separated from low-level analog, clocks, communication lines, and feedback nodes.

## Power Integrity

- IC power pins should have local high-frequency decoupling matched to the datasheet and package pinout, plus bulk capacitance for load transients.
- PDN-sensitive rails should have a clear source, load current budget, bulk/local capacitor placement, and expected ripple/noise target.
- Ferrite beads or filters between analog and digital supplies must include DC current rating, impedance target, damping/stability considerations, and local decoupling on both sides where needed.
- Test points for important rails should allow ripple/noise probing without creating large loops or adding excessive parasitic capacitance.

## Measurement And Bring-Up

- Scope probing plans should specify ground-spring/differential probing for fast edges and ripple; long ground leads can create misleading ringing.
- Bring-up should include measured rail ripple, switching-node stress, clock quality, communication waveforms, reset/boot timing, and interface error rate where relevant.
- If only schematic evidence is available, impedance, crosstalk, return-path, EMI, and PDN target-impedance conclusions remain `manual_review`.

## Source Notes

- Enriched from signal/power integrity material, sampling/reconstruction notes, and project bring-up test reports.
