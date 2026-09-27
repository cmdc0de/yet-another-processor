# power m4

Features: POWER-009

## Intent

5 V I/O net **IO5** and 3.3 V **IO33**, with `LVLSH` between them. ngspice: 5 V on HV → ~3.3 V on LV; 3.3 V on LV → ~5 V on HV. m1–m3 LDO/EN tests still pass. AP2112 unchanged.

## Work

- `hw/power/`: `LVLSH` subckt + test `.cir`.
- unittest `compiler/tests/test_power_m4.py`; m1–m3 still green.

## Done

- POWER-009: nets IO5 and IO33 exist; shifter translates 5 V ↔ 3.3 V in sim

## Out of scope

POWER-011 (bench). No USB PHY. No MOSFET 5 V cells (`CELL-019`).
