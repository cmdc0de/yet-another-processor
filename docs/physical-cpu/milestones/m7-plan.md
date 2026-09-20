# physical-cpu m7

Features: PHYSICAL-CPU-012

## Intent

IC GPR bank `r16`–`r31`, 1-bit slice. 16 IC register bits (one write, per-register `WE`). Two combinational read ports `qa` / `qb`. New slice `hw/rf-ic/`. KiCad 6 parsed as text. Spice uses a behavioral `ICREG` (or equivalent), **not** `LATCH`. Read mux may use CELL `MUX2`/`TG` as glue. m1–m6 still pass. Same VOL/VOH, 5 pF on `qa` and `qb`.

## Work

- `hw/rf-ic/*.kicad_sch`: 16 IC register symbols (`r16`–`r31`), not `yap_cells:LATCH`. Nets `d`, `qa`, `qb`, `we16`–`we31` (one-hot write), `ra16`–`ra31` and `rb16`–`rb31` (one-hot read), `VDD`, `VSS`. Comment names `LAT=2`.
- `hw/rf-ic/*_test.cir`: 16 `ICREG` (or equivalent) instances; two read muxes; no `LATCH` as the storage cell.
- unittest `compiler/tests/test_physical_cpu_m7.py`.

## Done

- PHYSICAL-CPU-012: 16 IC bits, two read ports, one write; ngspice write `r16`=1 and `r17`=0, then `qa` from `r16` at VOH and `qb` from `r17` at VOL after `WE`=0

## Out of scope

PHYSICAL-CPU-013–015, later-generation 016–020. No MOSFET `LATCH` bank, no named commercial IC, no 5-bit decoder, no 32-bit copies, no microcode stall.
