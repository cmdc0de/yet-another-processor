# memory-bus m1 walkthrough

Checkout: the tree after this commit. Commands assume repo root. Needs Python 3 and **Icarus Verilog** (`iverilog`, `vvp` on `PATH`).

```bash
python3 -m unittest compiler.tests.test_memory_bus_m1 -v
```

Expected: `Ran 6 tests ... OK`.

## MEMORY-BUS-001 — LAT_MEM=1

```bash
python3 -m unittest compiler.tests.test_memory_bus_m1.TestMemoryBusM1.test_MEMORY_BUS_001
```

After `we` on clock 0, SRAM word is still 0 (not combinational). After clock 1 the word is stored; `rdata` is not valid on the command cycle.

## MEMORY-BUS-002 — CPU port

```bash
python3 -m unittest compiler.tests.test_memory_bus_m1.TestMemoryBusM1.test_MEMORY_BUS_002
```

RTL and bench use `addr[31:0]`, `size` 1/2/4, `re`, `we`.

## MEMORY-BUS-006 — hw/bus tree

```bash
python3 -m unittest compiler.tests.test_memory_bus_m1.TestMemoryBusM1.test_MEMORY_BUS_006
```

`hw/bus/` contains Verilog-2001 `.v` files.

## MEMORY-BUS-007 — word roundtrip

```bash
python3 -m unittest compiler.tests.test_memory_bus_m1.TestMemoryBusM1.test_MEMORY_BUS_007
```

Store word `0xA5A5A5A5` at an aligned address; load word returns `0xA5A5A5A5`.

## MEMORY-BUS-008 — Icarus required

```bash
python3 -m unittest compiler.tests.test_memory_bus_m1.TestMemoryBusM1.test_MEMORY_BUS_008
```

Fails if `iverilog` or `vvp` is not on `PATH`.

## MEMORY-BUS-009 — 3.3 V

```bash
python3 -m unittest compiler.tests.test_memory_bus_m1.TestMemoryBusM1.test_MEMORY_BUS_009
```

HDL states VDD=3.3; no 5-volt SRAM model.
