# physical-cpu m8

Features: PHYSICAL-CPU-013

## Intent

Microcode ROM **256×64** and 8-bit `uPC` sequencer. New slice `hw/ucode/`. KiCad 6 parsed as text. Spice is behavioral ICs (not CELL `LATCH` as the ROM). Reset `uPC=0`. `seq=NEXT` increments `uPC`. m1–m7 still pass. Same VOL/VOH.

## Work

- `hw/ucode/*.kicad_sch`: nets `upc0`–`upc7`, `cw0`–`cw63` (control word, bit 0 = LSB), `clk`, `seq0`–`seq2`, `VDD`, `VSS`. Comment `256×64`. ROM is an IC symbol, not `yap_cells:LATCH`.
- `hw/ucode/*_test.cir`: 8-bit `uPC`; ROM contents at address 0 and 1; NEXT on clock.
- unittest `compiler/tests/test_physical_cpu_m8.py`.

## Done

- PHYSICAL-CPU-013: schematic is 256×64 with 8-bit `uPC`; ngspice reset `uPC=0`, ROM[0] `seq=NEXT`, after `clk` `uPC=1` and ROM[1] is a different word (VOL/VOH)

## Out of scope

PHYSICAL-CPU-014–015, later-generation 016–020. No DISPATCH/GOTO/HALT/TRAP, no memory port, no ALU, no caches.
