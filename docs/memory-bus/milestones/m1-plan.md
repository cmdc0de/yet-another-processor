# memory-bus m1

Features: MEMORY-BUS-001, MEMORY-BUS-002, MEMORY-BUS-006, MEMORY-BUS-007, MEMORY-BUS-008, MEMORY-BUS-009

## Intent

Verilog-2001 + Icarus in `hw/bus/`: CPU port (`addr`, `wdata`/`rdata`, `size`, `re`, `we`), `LAT_MEM=1`, 3.3 V. One aligned word store then load returns the stored value. Missing `iverilog`/`vvp` fails tests.

## Work

- `hw/bus/rtl/` transceiver + behavioral SRAM; `hw/bus/sim/` testbench.
- unittest `compiler/tests/test_memory_bus_m1.py` (or a `hw/bus` driver the tests invoke).
- VDD=3.3 in the HDL/`design.md` rails (no 5 V model).

## Done

- MEMORY-BUS-001: command this cycle, data next (`LAT_MEM=1`)
- MEMORY-BUS-002: port has `addr`, `size` ∈ {1,2,4}, `re`, `we`
- MEMORY-BUS-006: sources under `hw/bus/`
- MEMORY-BUS-007: aligned word write-then-read matches
- MEMORY-BUS-008: missing Icarus fails (not skip)
- MEMORY-BUS-009: bus/SRAM VDD is 3.3 V

## Out of scope

MEMORY-BUS-003–005 (DQ Hi-Z idle, byte lanes, `CE#`/`OE#`/`WE#`). Later-generation 010–012.
