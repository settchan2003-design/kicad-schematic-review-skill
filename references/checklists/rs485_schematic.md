# RS-485 Schematic Checklist

Apply this checklist when the schematic contains RS-485, RS-422, differential A/B bus pins, half-duplex transceivers, full-duplex transceivers, isolated fieldbus nodes, or direction-control pins such as `DE` and `/RE`.

## Net And Pin Logic

- [ ] RS-485 transceiver supply pins must connect to the voltage rail allowed by the selected transceiver datasheet.
- [ ] RS-485 transceiver ground pins must connect to the reference node required by the selected transceiver datasheet.
- [ ] Half-duplex transceivers must have driver-enable and receiver-enable states defined by controller pins, pull resistors, or fixed logic states.
- [ ] A receiver-enable pin that is active-low must not be left floating.
- [ ] A driver-enable pin must not be left floating.
- [ ] Full-duplex transceivers must connect driver output pair and receiver input pair to distinct bus pairs.
- [ ] A/B polarity must be consistent across every transceiver, connector, protection network, and termination network.

## Required Topology

- [ ] The RS-485 bus must include termination across the differential pair when the system requires a terminated bus.
- [ ] For a 120 $\Omega$ characteristic-impedance bus, each end termination resistor must be $R_T = 120\Omega$.
- [ ] A noise-filtered termination option must use matched resistor values on both signal conductors.
- [ ] The SLLA272D filtered termination example must use two $60\Omega$ resistors and $220\text{pF}$ filter capacitors.
- [ ] If external idle-bus failsafe biasing is required, the bus must include a bias network that creates $V_{AB} \ge 200\text{mV} + V_{NOISE}$.
- [ ] If remote nodes are powered from separate grounds and ground-potential difference exceeds the transceiver common-mode range, the schematic must include signal isolation and isolated power for the remote transceiver domain.
- [ ] If the selected transceiver lacks the required IEC/ESD rating, the bus pins must include an external protection network.

## Component Parameter Bounds

- [ ] Termination resistance must match the selected bus characteristic impedance: $R_T = Z_0$.
- [ ] Common RS-485 termination for $Z_0 = 120\Omega$ must use $R_T = 120\Omega$ at each terminated end.
- [ ] Filtered termination using two equal resistors must satisfy $R_{T1} = R_{T2}$.
- [ ] The SLLA272D filtered termination example resistor values must satisfy $R_{T1} = R_{T2} = 60\Omega$.
- [ ] The SLLA272D filtered termination example capacitor values must satisfy $C_{F1} = C_{F2} = 220\text{pF}$.
- [ ] External failsafe differential voltage must satisfy $V_{AB} = 200\text{mV} + V_{NOISE}$.
- [ ] For $V_{BUS(min)} = 4.75\text{V}$, $V_{AB} = 0.25\text{V}$, and $Z_0 = 120\Omega$, each failsafe bias resistor must be $R_B = 523\Omega$ when using the SLLA272D example network.
- [ ] Standard RS-485 unit loading must satisfy $N \le 32 / UL_{TRANSCEIVER}$ when no external failsafe bias loading is included.
- [ ] With external failsafe biasing modeled as 20 unit loads, node count must satisfy $N \le (32 - 20) / UL_{TRANSCEIVER}$.
- [ ] For $UL_{TRANSCEIVER} = 1/8$, external failsafe biasing limits the bus to $N \le 96$ transceivers.

## Absolute Maximum Ratings

- [ ] Bus common-mode voltage at each transceiver input must remain inside the selected transceiver absolute maximum and recommended operating common-mode ranges.
- [ ] Differential input voltage at each receiver must remain inside the selected transceiver absolute maximum range.
- [ ] Driver output current under termination and failsafe loading must remain below the selected transceiver output-current limit.
- [ ] Protection-device working voltage on A/B lines must exceed the maximum normal bus voltage.

## Source Notes

- Distilled from TI SLLA272D RS-485 design guidance.
