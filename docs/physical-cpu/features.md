# Physical CPU features

Prefix: `PHYSICAL-CPU`

Discrete MOSFET CPU that implements `docs/cpu/design.md`. Same programmer model as the FPGA CPU and `yap_cpu`. Cells come from `lt-spice/yap_cells.lib` (IRLML6246 / IRLML6401, 3.3 V).

Not FPGA-CPU. Not MOSFET cell characterization (done). Not board SRAM protocol (Memory + bus).

v1 is schematic + ngspice of each slice so features are testable before fab. Connector pinouts and KiCad version are `design.md` after this catalog.

## Tree

| ID | Feature | Status | Milestone |
|----|---------|--------|-----------|
| PHYSICAL-CPU-001 | ~~KiCad sources under `hw/`~~ | done | m1 |

## 1-bit slices

| ID | Feature | Status | Milestone |
|----|---------|--------|-----------|
| PHYSICAL-CPU-002 | ~~1-bit static latch schematic (CELL latch: EN high = load)~~ | done | m1 |
| PHYSICAL-CPU-003 | ~~Latch ports: D, EN, Q, VDD, VSS~~ | done | m1 |
| PHYSICAL-CPU-004 | ~~Latch netlist in ngspice: EN=1 Q follows D; EN=0 Q holds~~ | done | m1 |
| PHYSICAL-CPU-005 | ~~1-bit FLAGS latch schematic (Z/N/C/V bit; WE from control)~~ | done | m2 |
| PHYSICAL-CPU-006 | ~~1-bit full adder schematic: `a`, `b`, `cin`, `sum`, `cout`~~ | done | m2 |
| PHYSICAL-CPU-007 | ~~Adder netlist matches CELL-012 truth table at VOL/VOH~~ | done | m2 |

## Datapath width

| ID | Feature | Status | Milestone |
|----|---------|--------|-----------|
| PHYSICAL-CPU-008 | ~~32-bit adder: 32 copies of the adder bit, ripple `cin`/`cout`~~ | done | m3 |
| PHYSICAL-CPU-009 | ~~32-bit MOSFET register: 32 latches, one write-enable~~ | done | m4 |
| PHYSICAL-CPU-010 | ~~Wired constants: `r0`=0, `r1`=1, `r2`=all-ones (no latches)~~ | done | m5 |
| PHYSICAL-CPU-011 | ~~MOSFET GPR bank `r3`–`r15`, two read ports, one write, `LAT=1`~~ | done | m6 |
| PHYSICAL-CPU-012 | ~~IC GPR bank `r16`–`r31`, two read ports, one write, `LAT=2`~~ | done | m7 |

## Control and host port

| ID | Feature | Status | Milestone |
|----|---------|--------|-----------|
| PHYSICAL-CPU-013 | ~~Microcode ROM 256×64 and `uPC` sequencer (ICs allowed)~~ | done | m8 |
| PHYSICAL-CPU-014 | ~~CPU memory port: addr, data, size, re, we (`docs/cpu/design.md`)~~ | done | m9 |
| PHYSICAL-CPU-015 | ~~Integer ALU ops on the MOSFET datapath (add/sub/logic; shifts/mul/div may be IC)~~ | done | m10 |

## Later generation (do not pull into m1)

| ID | Feature | Status | Milestone |
|----|---------|--------|-----------|
| PHYSICAL-CPU-016 | Fabricate/order a named latch or adder PCB | open | later-generation |
| PHYSICAL-CPU-017 | Assemble SOT-23 and bring up on the bench | open | later-generation |
| PHYSICAL-CPU-018 | Same YAP1 as FPGA-CPU reaches halt on the physical machine | open | later-generation |
| PHYSICAL-CPU-019 | Caches | open | later-generation |
| PHYSICAL-CPU-020 | Pipelined control | open | later-generation |
