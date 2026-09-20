# Memory + bus design (v1)

Protocol between the CPU memory port (`docs/cpu/design.md` CPU-015) and SRAM. `LAT_MEM=1`: command this cycle, data next. Not Physical CPU slices. Not FPGA board SRAM. Not GPU/MCU.

## Rails

| Knob | v1 |
|------|----|
| VDD | 3.3 V |
| VSS | 0 V (net **VSS**) |
| SRAM | 3.3 V (no 5 V part on v1) |

## CAD

| Knob | v1 |
|------|----|
| HDL | Verilog IEEE 1364-2001 |
| Simulator | Icarus Verilog (`iverilog` then `vvp`) |
| Host | Linux |
| Clock | `clk` rising edge |
| Reset | synchronous, active-high `rst` |

Missing `iverilog`/`vvp` fails tests. No GUI. Behavioral SRAM model; not a vendor part.

## Tree

```
hw/bus/
  rtl/     transceiver + SRAM control + behavioral SRAM
  sim/     testbench + Python driver if needed
```

## CPU port (unchanged)

```
addr[31:0]   byte address, naturally aligned for size
wdata[31:0]  store, low `size` bytes, LE
rdata[31:0]  load, low `size` bytes, LE
size[2:0]    1, 2, or 4
re, we
```

Window/align traps stay **inside the CPU**. This bus does not trap.

## SRAM pins

| Net | Polarity | Meaning |
|-----|----------|---------|
| A | — | word address = `addr[31:2]` |
| DQ[31:0] | tristate | bidirectional data |
| CE# | active-low | 0 when `re` or `we` |
| OE# | active-low | 0 when `re` and not `we` |
| WE# | active-low | 0 when `we` |
| BE[3:0] | active-high | byte enables, LE |

Never `WE#=0` and `OE#=0` together. Idle: CE#=OE#=WE#=1, DQ Hi-Z.

### Byte enables (aligned)

| size | addr[1:0] | BE[3:0] |
|------|-----------|---------|
| 4 | 00 | 1111 |
| 2 | 00 | 0011 |
| 2 | 10 | 1100 |
| 1 | 00 | 0001 |
| 1 | 01 | 0010 |
| 1 | 10 | 0100 |
| 1 | 11 | 1000 |

BE[0] is the byte at the lowest address (LE).

## Cycles (`LAT_MEM=1`)

**Store:** cycle 0: `we=1`, addr/size/wdata valid, CPU drives DQ, WE#=0. Cycle 1: SRAM has the bytes; `we=0`, DQ Hi-Z.

**Load:** cycle 0: `re=1`, addr/size valid, OE#=0, CPU DQ Hi-Z. Cycle 1: SRAM drives DQ, `rdata` valid.

`re` and `we` are mutually exclusive.

## Glue

- Store: CPU transceiver drives `DQ` from `wdata`.
- Load: transceiver samples `DQ` onto `rdata`.
- Idle: transceiver Hi-Z.

## Out of this document

Named SRAM vendor/part, PCB, 5 V I/O, burst/page mode, DMA, caches.
