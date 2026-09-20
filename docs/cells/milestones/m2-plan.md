# cells m2

Features: CELL-006, CELL-007, CELL-008, CELL-009, CELL-010, CELL-011

## Intent

Finish the combinational MOSFET family on the same ngspice harness as m1: NOR, AND, OR, XOR, transmission gate, 2:1 mux. Subcircuits instantiate IRLML6246/IRLML6401 (XOR may use TGs). After settle, 5 pF load, VOL ≤ 0.3 V / VOH ≥ 3.0 V. m1 tests still pass.

## Work

- `.subckt` NOR, AND, OR, XOR, TG, MUX2 in `lt-spice/yap_cells.lib`. AND/OR may be NAND/NOR + inverter.
- XOR is MOSFET (TG XOR allowed). MAX4610 is allowed only for the TG/mux cell (CELL-010), not as the ALU XOR.
- Test `.cir` files; unittest `compiler/tests/test_cells_m2.py` runs `ngspice -b`.

## Done

- CELL-006: NOR truth table at VOH/VOL
- CELL-007: AND truth table at VOH/VOL
- CELL-008: OR truth table at VOH/VOL
- CELL-009: XOR truth table at VOH/VOL
- CELL-010: TG on (path conducts, out follows in within levels) and off (out not driven to the opposite rail by the TG)
- CELL-011: 2:1 mux: S=0 → Y=A; S=1 → Y=B, at VOH/VOL

## Out of scope

CELL-003, 012–013, 015–017, later-generation 019–021.
