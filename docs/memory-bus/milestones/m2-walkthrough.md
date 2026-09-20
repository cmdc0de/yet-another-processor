# memory-bus m2 walkthrough

Checkout: the tree after this commit. Commands assume repo root. Needs Python 3 and **Icarus Verilog** (`iverilog`, `vvp` on `PATH`).

```bash
python3 -m unittest compiler.tests.test_memory_bus_m2 compiler.tests.test_memory_bus_m1 -v
```

Expected: `Ran 9 tests ... OK`. m1 still passes.

## MEMORY-BUS-003 — DQ tristate

```bash
python3 -m unittest compiler.tests.test_memory_bus_m2.TestMemoryBusM2.test_MEMORY_BUS_003
```

Idle: `DQ` is Hi-Z. During `we`, CPU drives `DQ`. After `LAT_MEM=1` on a load, SRAM data appears on `DQ`.

## MEMORY-BUS-004 — LE byte lanes

```bash
python3 -m unittest compiler.tests.test_memory_bus_m2.TestMemoryBusM2.test_MEMORY_BUS_004
```

Word `0xA5A5A5A5` at addr 0, then byte `size=1` `wdata=0x5A` at addr 0: bytes 1–3 stay `A5`. Half `size=2` at addr 2 does not change bytes 0–1.

## MEMORY-BUS-005 — CE# / OE# / WE#

```bash
python3 -m unittest compiler.tests.test_memory_bus_m2.TestMemoryBusM2.test_MEMORY_BUS_005
```

Store: `ce_n=0`, `we_n=0`, `oe_n=1`. Load: `ce_n=0`, `oe_n=0`, `we_n=1`. Idle: all 1.
