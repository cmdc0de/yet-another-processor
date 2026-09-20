# physical-cpu m1

Features: PHYSICAL-CPU-001, PHYSICAL-CPU-002, PHYSICAL-CPU-003, PHYSICAL-CPU-004

## Intent

Stand up `hw/latch/`: a KiCad 6 schematic of the CELL latch (EN high = load) with ports D, EN, Q, VDD, VSS, and an ngspice bench that proves follow and hold. No `kicad-cli`. Missing `ngspice` fails electrical tests. Same VOL/VOH as `docs/cells/design.md`.

## Work

- `hw/latch/*.kicad_sch` (KiCad 6 s-expr). Nets named D, EN, Q, VDD, VSS. Header pin order VDD, VSS, D, EN, Q.
- `hw/latch/*_test.cir` instantiates `yap_cells.lib` `LATCH` with those port names; 3.3 V, 5 pF on Q.
- Unittest `compiler/tests/test_physical_cpu_m1.py`: parse schematic as text; `ngspice -b` for follow/hold (reuse CELL-013/016 timing idea).

## Done

- PHYSICAL-CPU-001: `hw/` contains the latch KiCad sources
- PHYSICAL-CPU-002: schematic is a 1-bit static latch (CELL latch, EN high = load)
- PHYSICAL-CPU-003: schematic nets include D, EN, Q, VDD, VSS
- PHYSICAL-CPU-004: ngspice: EN=1 Q follows D; EN=0 Q holds (VOL/VOH)

## Out of scope

PHYSICAL-CPU-005–015, later-generation 016–020.
