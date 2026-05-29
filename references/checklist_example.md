# Baseline Schematic Review Checklist

Apply this baseline checklist to every schematic review. Keep domain-specific rules in `references/checklists/*.md`.

## Component Fields

- Every production component must have a non-empty Reference.
- Every production component must have a concrete Value.
- Placeholder values such as `R`, `C`, `L`, `D`, `Q`, `U`, and `J` should be replaced.
- Every production component should have a Footprint.
- Datasheet should be filled for ICs, connectors, regulators, and special parts.

## Connectivity

- The schematic should not contain unintentionally floating pins.
- Intentional unconnected pins should use no-connect markers.
- Power rails should use clear and consistent net names.
- Global labels should be used only when cross-sheet connectivity is intended.

## Power

- Power inputs should show polarity and expected voltage.
- Regulators should include input and output capacitors according to datasheets.
- IC power pins should have nearby decoupling capacitors.
- IC supply rails should stay within recommended operating conditions from datasheets.
- Exposed pads and special ground pins should follow datasheet guidance.

## IC Datasheet Checks

- Each IC should have a matching local datasheet or a clear datasheet path in the schematic.
- Reset, enable, boot, mode, address, and strap pins should have intentional states.
- Required reference, regulator, charge-pump, or internal LDO capacitors should be present.
- Clock, crystal, and oscillator pins should match datasheet requirements.
- Unused IC pins should follow datasheet guidance.
- Interface pins should connect to compatible voltage domains.
- Differential or high-speed signals should preserve polarity and required termination.

## Manufacturing

- Components excluded from BOM or board should be intentional.
- Footprints should match package and assembly intent.
- Test points should be considered for important rails and programming/debug signals.
