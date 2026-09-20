# Physical CPU design (v1)

Schematic + ngspice of each slice. Implements `docs/cpu/design.md` using `docs/cells/design.md`. Fabrication is later-generation.

Not FPGA-CPU. Not Memory + bus protocol. Not 5 V I/O.

## Rails and parts

Same as the cell library:

| Knob | v1 |
|------|----|
| VDD | 3.3 V |
| VSS | 0 V (net name **VSS**) |
| N-FET | IRLML6246, SOT-23 footprint `MICRO3_SOT23_INF` |
| P-FET | IRLML6401, SOT-23 footprint `MICRO3_SOT23_INF` |
| VOL / VOH | ≤ 0.3 V / ≥ 3.0 V, 5 pF load |
| Latch | CELL `LATCH`: EN high = transparent |

## CAD

| Knob | v1 |
|------|----|
| Schematic | KiCad **6** s-expression `.kicad_sch` |
| Footprints | `docs/footprints-and-models/KiCADv6/` |
| Tests | Parse schematic as text; **do not** require `kicad-cli` or a GUI |
| Electrical | ngspice `-b` on a `.cir` that instantiates the matching `yap_cells.lib` subckt |

The `.cir` is the sim view of that slice (connectors + cell). It must use the same port names as the schematic. Missing `ngspice` fails electrical tests.

## Tree

```
hw/
  latch/     1-bit latch slice (m1)
  adder/     1-bit adder (later)
  ...
```

Each slice: `*.kicad_sch` plus `*_test.cir` (or equivalent) for ngspice.

## Latch slice ports (PHYSICAL-CPU-003)

| Net | Direction |
|-----|-----------|
| D | in |
| EN | in (active-high load) |
| Q | out |
| VDD | 3.3 V |
| VSS | 0 V |

Header: 2.54 mm, one pin per net, order **VDD, VSS, D, EN, Q**.

FLAGS bit (PHYSICAL-CPU-005) is the same latch; WE is EN, D is the flag value.

## Adder slice ports (PHYSICAL-CPU-006)

`a`, `b`, `cin`, `sum`, `cout`, VDD, VSS. Spice truth table = CELL-012.

## Out of this document

Gerbers, fab vendor, MCU/FPGA host adapter, SRAM tristate timing, 32-bit connector, IC GPR part number.
