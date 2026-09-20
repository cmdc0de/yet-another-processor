# physical-cpu m5

Features: PHYSICAL-CPU-010

## Intent

Hardwired constant GPRs: `r0` = 0, `r1` = 1 (bit 0 = LSB), `r2` = all-ones. No `LATCH` cells. New slice `hw/wired/`. KiCad 6 parsed as text; ngspice confirms rail ties at VOL/VOH. m1–m4 tests still pass.

## Work

- `hw/wired/*.kicad_sch`: nets `r0_0`–`r0_31`, `r1_0`–`r1_31`, `r2_0`–`r2_31`, `VDD`, `VSS`. `r0_*` to `VSS`; `r1_0` to `VDD` and `r1_1`–`r1_31` to `VSS`; `r2_*` to `VDD`. No `LATCH`.
- `hw/wired/*_test.cir`: same ties (no `LATCH`); DC voltages on those nets.
- unittest `compiler/tests/test_physical_cpu_m5.py`.

## Done

- PHYSICAL-CPU-010: schematic and spice have no latches; ngspice `r0` all VOL, `r1` = 0x1, `r2` all VOH

## Out of scope

PHYSICAL-CPU-011–015, later-generation 016–020. No two-port banks, no `LAT=1`/`LAT=2`.
