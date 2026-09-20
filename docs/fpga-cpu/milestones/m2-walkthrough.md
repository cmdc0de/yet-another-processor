# fpga-cpu m2 walkthrough

Checkout: the tree after this commit. Commands assume repo root. Needs Python 3 and Icarus Verilog (`iverilog`, `vvp` on `PATH`).

```bash
python3 -m unittest compiler.tests.test_fpga_cpu_m2 compiler.tests.test_fpga_cpu_m1 -v
```

Expected: `Ran 10 tests ... OK`. m1 still passes; a `nop`-only image with `--max-cycles 8` still exits non-zero.

## FPGA-CPU-007 — split RF latency

```bash
python3 -m unittest compiler.tests.test_fpga_cpu_m2.TestFpgaCpuM2.test_FPGA_CPU_007
```

Two YAP1s as in cpu m2 CPU-032: `add t0, t0, one; halt` vs `add s0, s0, one; halt`. Sim `cycles` for the `s0` (IC bank) image is greater.

## FPGA-CPU-008 — dump matches yap_cpu

```bash
python3 -m unittest compiler.tests.test_fpga_cpu_m2.TestFpgaCpuM2.test_FPGA_CPU_008
```

`add t0, one, one; halt`. Sim dump `pc`, `flags`, and `r10` equal `yap_cpu` after `run()`.

## FPGA-CPU-009 — integer ALU

```bash
python3 -m unittest compiler.tests.test_fpga_cpu_m2.TestFpgaCpuM2.test_FPGA_CPU_009
```

Same images as cpu m2 CPU-008, 009, 011, 012, 013 (`and`/`xor`, `sll`/`sra`, `mul`/`div` with ÷0 → 0 and Z=1, `addi`/`andi`/`lui`, `adr t0, 4` → `t0==8`). Sim GPRs and FLAGS match `yap_cpu`.
