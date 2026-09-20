# cells m1

Features: CELL-001, CELL-002, CELL-004, CELL-005, CELL-014, CELL-018

## Intent

Stand up the MOSFET library in `lt-spice/` as ngspice netlists: 3.3 V rails, IRLML6246/IRLML6401 models, a CMOS inverter and 2-input NAND. Python runs `ngspice -b` with no GUI. After settle, outputs meet VOL ≤ 0.3 V / VOH ≥ 3.0 V with 5 pF load (`docs/cells/design.md`).

## Work

- Text SPICE models for IRLML6246 (N) and IRLML6401 (P) in `lt-spice/`. Subcircuits instantiate those parts, not AO3400/AO3401A.
- `INVERTER` and `NAND` `.subckt`s; test `.cir` files, VDD=3.3, VSS=0, CL=5 pF.
- Python unittest (`compiler/tests/test_cells_m1.py` or under `lt-spice/`) runs `ngspice -b`, asserts truth table and VOH/VOL. Missing `ngspice` fails, does not skip.

## Done

- CELL-001: test netlists set VDD to 3.3 V and VSS to 0
- CELL-002: library contains named N and P models used by the inverter and NAND
- CELL-004: inverter 0 in → out ≥ 3.0 V; 1 in → out ≤ 0.3 V
- CELL-005: NAND truth table (00/01/10 → 1, 11 → 0) at those levels
- CELL-014: those outputs meet VOL ≤ 0.3 V, VOH ≥ 3.0 V
- CELL-018: `python3 -m unittest …` runs `ngspice -b` (no GUI)

## Out of scope

CELL-003, 006–013, 015–017, later-generation 019–021.
