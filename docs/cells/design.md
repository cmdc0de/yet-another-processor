# MOSFET cell library design (v1)

CMOS cells at the 3.3 V CPU core. Implementation lives in `lt-spice/`. Physical CPU boards (`hw/`) are a later sequence.

Not 5 V I/O, not KiCad layouts, not bench measurements.

## Rails

| Knob | v1 |
|------|----|
| VDD | **3.3 V** |
| VSS | **0 V** |
| Logic 0 in tests | 0 V |
| Logic 1 in tests | 3.3 V |
| Load on each characterized output | **5 pF** to VSS |

## Devices

| Role | Part | Package |
|------|------|---------|
| N-channel | Infineon **IRLML6246** | SOT-23 |
| P-channel | Infineon **IRLML6401** | SOT-23 |
| Analog mux / extra TG | Maxim **MAX4610** (quad SPST) | as in `docs/componets/` |

Models are **text SPICE** in `lt-spice/` (extend `ltspice_cmdc0de.lib`). Subcircuits must instantiate IRLML6246 / IRLML6401 (or MAX4610 where that row applies), not AO3400/AO3401A.

XOR and the adder are MOSFET cells (transmission-gate XOR is allowed). MAX4610 is the CELL-010 mux/TG option, not a substitute for the ALU XOR.

## Levels (CELL-014)

After settling, with the 5 pF load:

| | |
|--|--|
| VOL | **≤ 0.3 V** |
| VOH | **≥ 3.0 V** |

No Vil/Vih sweep in v1. Inputs are rails.

## Latch (CELL-013)

1-bit **static D-latch**. **EN active-high**: EN=1 transparent (Q follows D); EN=0 hold. Level-sensitive, not an edge flop.

## Adder (CELL-012 / CELL-017)

1-bit full adder, ports `a`, `b`, `cin`, `sum`, `cout`. Truth table including **0+0+0 → sum=0,cout=0** and **1+1+1 → sum=1,cout=1**. MOSFET cells only.

## Simulator and tree

| Knob | v1 |
|------|----|
| Simulator | **ngspice** batch (`ngspice -b`) |
| Host | Linux, no GUI |
| Netlist | SPICE `.cir` / `.subckt` |
| LTspice `.asc` / `.asy` | optional human schematics; tests must not require LTspice |

```
lt-spice/
  *.subckt / lib    cell netlists + MOSFET models
  *_test.cir        one test netlist per cell (or a shared bench)
```

Python (unittest under `compiler/tests/` or a driver next to the netlists) runs `ngspice -b`, reads the listing/raw, asserts VOL/VOH and the truth table. Missing `ngspice` is a failed test, not a skip.

This host does not currently have `ngspice` on `PATH`. Implement-m needs it installed like FPGA-CPU needed `iverilog`.

## Out of this document

KiCad footprints (already under `docs/footprints-and-models/`), PCB, 5 V shifters, measured delay, Physical CPU bit-slice boards.
