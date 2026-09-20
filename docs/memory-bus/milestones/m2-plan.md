# memory-bus m2

Features: MEMORY-BUS-003, MEMORY-BUS-004, MEMORY-BUS-005

## Intent

Expose the SRAM-side bus from `docs/memory-bus/design.md`: tristate `DQ[31:0]`, LE byte enables, active-low `CE#`/`OE#`/`WE#`. Keep `LAT_MEM=1` and the m1 word roundtrip. Verilog-2001 + Icarus. m1 tests still pass.

## Work

- `hw/bus/rtl/`: `DQ`, `ce_n`, `oe_n`, `we_n`, `be[3:0]`; store drives DQ, load SRAM drives DQ, idle Hi-Z. Never `we_n` and `oe_n` both 0.
- Byte enables per the design table (`size` 1/2/4, aligned `addr[1:0]`).
- unittest `compiler/tests/test_memory_bus_m2.py`; m1 still green.

## Done

- MEMORY-BUS-003: idle DQ is Hi-Z; store CPU drives; load SRAM drives
- MEMORY-BUS-004: size 1/2/4 writes/reads only the LE low lanes (other bytes unchanged)
- MEMORY-BUS-005: `CE#`/`OE#`/`WE#` derived from `re`/`we` as in `design.md`

## Out of scope

Later-generation 010–012. No named SRAM IC, no burst, no DMA.
