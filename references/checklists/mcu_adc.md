# MCU, ADC, And Low-Level Signal Checklist

Apply this checklist when the schematic contains an MCU, ADC, sensor analog front end, crystal/oscillator, programming connector, low-level measurement input, or text/net names implying `ADC`, `AIN`, `VREF`, `VCAP`, `SWD`, `JTAG`, `BOOT`, `NRST`, `XTAL`, or `OSC`.

## MCU Power And Startup

- Every MCU power pin and analog-power pin must have datasheet-required local decoupling; special regulator pins such as VCAP must use the specified capacitance and voltage rating.
- Reset, boot, mode, programming/debug, and strap pins must have intentional default states through pull-ups, pull-downs, or controller connections.
- Oscillator/crystal load capacitors, bias parts, and layout-sensitive crystal pins must match the datasheet and selected crystal parameters.
- Voltage domains must be checked for every interface pin, especially when MCU I/O connects to drivers, sensors, transceivers, or isolated circuits.

## ADC And Analog Inputs

- Divider values must keep ADC input voltage inside absolute maximum and recommended input range over worst-case sensor/input voltage.
- ADC source impedance and RC filter settling time must be compatible with sampling time, input sampling capacitance, and required accuracy.
- For SAR ADCs, check both the sampling capacitor charge kickback into the input capacitor and the final settling time through the source/filter resistance.
- Sequential ADC channel sampling should consider worst-case previous-channel voltage; high source impedance can produce channel-to-channel memory errors.
- Anti-alias filtering should be considered when sampled signals may contain frequency content above half the sampling rate.
- Reference pins and analog supply pins must have datasheet-required filtering, decoupling, and grounding treatment.
- Protection parts should be considered for external analog inputs, long cables, inductive environments, or user-accessible connectors.

## Layout And Testability

- Analog traces and references should be isolated from switch nodes, motor phases, clocks, and high-current loops; if PCB evidence is unavailable, keep this as `manual_review`.
- Important rails, reset/programming signals, references, and analog measurements should have test access unless the project intentionally omits it.
- Differential or precision measurement paths must preserve polarity, input filtering symmetry, and Kelvin/current-return assumptions where applicable.

## Source Notes

- Enriched from the hardware onboarding manual sections on MCU decoupling, VCAP, ADC front-end RC filters, anti-aliasing, and bring-up testing.
