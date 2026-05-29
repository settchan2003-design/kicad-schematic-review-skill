# I2C Pull-Up Schematic Checklist

Apply this checklist when the schematic contains I2C, SMBus-like open-drain SCL/SDA nets, pull-up resistors on open-drain serial lines, or mixed-voltage open-drain communication.

## Net And Pin Logic

- [ ] Every active I2C SCL net must have a pull-up path to the selected I2C pull-up reference voltage.
- [ ] Every active I2C SDA net must have a pull-up path to the selected I2C pull-up reference voltage.
- [ ] I2C devices connected to a bus must tolerate the selected pull-up reference voltage on their SCL and SDA pins.
- [ ] Open-drain I2C outputs must not be tied to a push-pull output on the same net unless the push-pull output is disabled or open-drain in the active mode.
- [ ] Level translators on I2C nets must have their reference rails connected to the intended voltage domains.

## Required Topology

- [ ] SCL and SDA must each have an effective pull-up resistance calculated from the parallel combination of all pull-up paths on that net.
- [ ] If multiple pull-up resistors exist on one I2C net, the effective value must be used: $R_{P(EQ)} = 1 / \sum_i(1/R_{P_i})$.
- [ ] If the bus crosses voltage domains, the schematic must include an I2C-compatible level translation topology or prove every connected pin tolerates the pull-up voltage.

## Component Parameter Bounds

- [ ] Minimum pull-up resistance must satisfy $R_{P(min)} = (V_{CC} - V_{OL(max)}) / I_{OL}$.
- [ ] Maximum pull-up resistance must satisfy $R_{P(max)} = t_r / (0.8473 \times C_b)$.
- [ ] The selected effective pull-up resistance must satisfy $R_{P(min)} \le R_{P(EQ)} \le R_{P(max)}$.
- [ ] Standard-mode I2C rise time must satisfy $t_r \le 1000\text{ns}$.
- [ ] Fast-mode I2C rise time must satisfy $t_r \le 300\text{ns}$.
- [ ] Fast-mode Plus I2C rise time must satisfy $t_r \le 120\text{ns}$.
- [ ] Standard-mode and Fast-mode bus capacitance must satisfy $C_b \le 400\text{pF}$.
- [ ] Fast-mode Plus bus capacitance must satisfy $C_b \le 550\text{pF}$.
- [ ] For $V_{CC} > 2\text{V}$, low-level output voltage must satisfy $V_{OL(max)} \le 0.4\text{V}$ at $I_{OL}=3\text{mA}$.
- [ ] For $V_{CC} \le 2\text{V}$ in Fast-mode and Fast-mode Plus, low-level output voltage must satisfy $V_{OL(max)} \le 0.2 \times V_{CC}$ at $I_{OL}=2\text{mA}$.
- [ ] For Fast-mode with $C_b = 200\text{pF}$ and $V_{CC}=3.3\text{V}$, the selected pull-up resistance must satisfy $966.667\Omega \le R_P \le 1.77\text{k}\Omega$.

## Absolute Maximum Ratings

- [ ] The I2C pull-up reference voltage must not exceed the absolute maximum voltage of any connected SCL or SDA pin.
- [ ] Sink current through each pull-up must not exceed the connected device's I2C low-level output current rating.
- [ ] Level-translator reference voltages must remain inside the level translator absolute maximum ratings.

## Source Notes

- Distilled from TI SLVA689 I2C pull-up resistor calculation guidance.
