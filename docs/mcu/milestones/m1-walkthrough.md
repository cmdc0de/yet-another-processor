# MCU I/O m1 walkthrough

Checkout: the tree after this commit. Commands assume repo root. Needs Python 3 and **Icarus Verilog** (`iverilog`, `vvp` on `PATH`).

```bash
python3 -m unittest compiler.tests.test_mcu_m1 -v
```

Expected: `Ran 7 tests ... OK`.

## MCU-001 — HDL tree

```bash
python3 -m unittest compiler.tests.test_mcu_m1.TestMcuM1.test_MCU_001
```

`hw/mcu/` contains Verilog-2001 `.v` files.

## MCU-002 — sim runs

```bash
python3 -m unittest compiler.tests.test_mcu_m1.TestMcuM1.test_MCU_002
```

`iverilog` + `vvp` of the MCU sim exits 0.

## MCU-003 — Icarus required

```bash
python3 -m unittest compiler.tests.test_mcu_m1.TestMcuM1.test_MCU_003
```

Fails if `iverilog` or `vvp` is not on `PATH`.

## MCU-004 — CPU port

```bash
python3 -m unittest compiler.tests.test_mcu_m1.TestMcuM1.test_MCU_004
```

Bench drives `clk`, `rst`, `we`, `re`, `addr[7:0]`, `wdata[31:0]`, `rdata[31:0]`.

## MCU-005 — command/status map

```bash
python3 -m unittest compiler.tests.test_mcu_m1.TestMcuM1.test_MCU_005
```

Sources name STATUS 0x00, KEY_DATA 0x04, SER_DATA 0x08, STOR_LBA 0x0C, STOR_IDX 0x10, STOR_DATA 0x14, STOR_CMD 0x18.

## MCU-006 — idle after reset

```bash
python3 -m unittest compiler.tests.test_mcu_m1.TestMcuM1.test_MCU_006
```

After reset, a STATUS read (offset 0x00) returns 0.

## MCU-011 — 3.3 V

```bash
python3 -m unittest compiler.tests.test_mcu_m1.TestMcuM1.test_MCU_011
```

HDL states VDD=3.3 (no 5 V MCU model).
