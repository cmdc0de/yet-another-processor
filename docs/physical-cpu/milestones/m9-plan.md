# physical-cpu m9

Features: PHYSICAL-CPU-014

## Intent

CPU memory port only: pins, not the SRAM board. New slice `hw/memport/`. KiCad 6 parsed as text. Spice is a behavioral 32-bit word at address 0 (IC SRAM model). `we` then `re` after one `clk` (`LAT_MEM=1`). m1–m8 still pass. Same VOL/VOH.

## Work

- `hw/memport/*.kicad_sch`: nets `addr0`–`addr31`, `wdata0`–`wdata31`, `rdata0`–`rdata31`, `sz0` `sz1` (`00`=byte/`size=1`, `01`=half/`size=2`, `10`=word/`size=4`), `re`, `we`, `clk`, `VDD`, `VSS`. Comment `LAT_MEM=1`.
- `hw/memport/*_test.cir`: word store then load at addr 0; rdata matches wdata after one clk.
- unittest `compiler/tests/test_physical_cpu_m9.py`.

## Done

- PHYSICAL-CPU-014: schematic has addr, wdata, rdata, size, re, we; ngspice `we` of a word, then `re` after `clk` returns that word at VOL/VOH

## Out of scope

PHYSICAL-CPU-015, later-generation 016–020. No ALU, no align/window trap hardware, no board SRAM protocol, no caches.
