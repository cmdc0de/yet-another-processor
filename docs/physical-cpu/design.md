# Physical CPU design (v1 + m11)

Schematic + ngspice of each slice. Implements `docs/cpu/design.md` using `docs/cells/design.md`. m11 is a KiCad PCB of the 1-bit latch (CAD, not a fab order).

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

| Knob | v1 | m11 |
|------|----|-----|
| Schematic | KiCad **6** s-expression `.kicad_sch` | same (CELL `LATCH` block) |
| PCB | not required | KiCad **6** `.kicad_pcb` (s-expr, text parse, no `kicad-cli`) |
| Footprints | `docs/footprints-and-models/KiCADv6/` | **`MICRO3_SOT23_INF`** for IRLML6246 / IRLML6401 |
| Tests | Parse schematic as text; **do not** require `kicad-cli` or a GUI | parse `.kicad_pcb` as text the same way |
| Electrical | ngspice `-b` on a `.cir` that instantiates the matching `yap_cells.lib` subckt | m1 `latch_test.cir` still passes |

The `.cir` is the sim view of that slice (connectors + cell). It must use the same port names as the schematic. Missing `ngspice` fails electrical tests.

## Tree

```
hw/
  latch/     1-bit latch slice (m1 schematic + spice; m11 `.kicad_pcb`)
  adder/     1-bit adder
  ...
```

Each slice: `*.kicad_sch` plus `*_test.cir` (or equivalent) for ngspice. m11 adds `hw/latch/*.kicad_pcb`.

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

## PCB (m11)

Named board is the **1-bit latch**. v1 schematic stays the CELL `LATCH` block. The PCB is the SOT-23 placement of that cell.

| Knob | m11 |
|------|-----|
| Path | `hw/latch/*.kicad_pcb` |
| N-FET | IRLML6246, `MICRO3_SOT23_INF` |
| P-FET | IRLML6401, `MICRO3_SOT23_INF` |
| Header | 2.54 mm, pin order **VDD, VSS, D, EN, Q** |
| Nets | **D**, **EN**, **Q**, **VDD**, **VSS** |

No black-box LATCH package on the PCB. No gerber plot. No fab vendor.

## Adder slice ports (PHYSICAL-CPU-006)

`a`, `b`, `cin`, `sum`, `cout`, VDD, VSS. Spice truth table = CELL-012.

## Out of this document

Gerbers, fab vendor, assemble/bench (PHYSICAL-CPU-017), adder PCB, MCU/FPGA host adapter, SRAM tristate timing, 32-bit connector, IC GPR part number.
