# physical-cpu m11

Features: PHYSICAL-CPU-016

## Intent

A named 1-bit latch PCB in KiCad 6: SOT-23 IRLML6246 / IRLML6401, header VDD VSS D EN Q. Tests parse `.kicad_pcb` as text. m1 latch ngspice still passes. No fab order.

## Work

- `hw/latch/*.kicad_pcb`: footprints `MICRO3_SOT23_INF`; values IRLML6246 and IRLML6401; nets D, EN, Q, VDD, VSS; 5-pin 2.54 mm header in that order.
- unittest `compiler/tests/test_physical_cpu_m11.py`; m1 still green.

## Done

- PHYSICAL-CPU-016: `hw/latch/` has a `.kicad_pcb` naming IRLML6246, IRLML6401, `MICRO3_SOT23_INF`, and nets D, EN, Q, VDD, VSS

## Out of scope

PHYSICAL-CPU-017 (assemble / bench), 018–020. Adder PCB. Gerber/fab vendor. `kicad-cli`.
