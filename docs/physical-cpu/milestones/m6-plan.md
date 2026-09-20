# physical-cpu m6

Features: PHYSICAL-CPU-011

## Intent

MOSFET GPR bank `r3`–`r15`, 1-bit slice. 13 CELL `LATCH` (one write, per-register `WE`). Two combinational read ports `qa` / `qb` muxed from those Qs (CELL `MUX2` and/or `TG`). New slice `hw/rf-mosfet/`. KiCad 6 parsed as text; ngspice on `yap_cells.lib`. m1–m5 still pass. Same VOL/VOH, 5 pF on `qa` and `qb`.

## Work

- `hw/rf-mosfet/*.kicad_sch`: 13 `LATCH` (`r3`–`r15`). Nets `d`, `qa`, `qb`, `we3`–`we15` (one-hot write), `ra3`–`ra15` and `rb3`–`rb15` (one-hot read), `VDD`, `VSS`. Comment names `LAT=1`.
- `hw/rf-mosfet/*_test.cir`: same ports; 13 `LATCH`; two read muxes.
- unittest `compiler/tests/test_physical_cpu_m6.py`.

## Done

- PHYSICAL-CPU-011: 13 MOSFET bits, two read ports, one write; ngspice write `r3`=1 and `r4`=0, then `qa` from `r3` at VOH and `qb` from `r4` at VOL after `WE`=0

## Out of scope

PHYSICAL-CPU-012–015, later-generation 016–020. No IC bank, no 5-bit index decoder, no 32-bit copies, no microcode stall.
