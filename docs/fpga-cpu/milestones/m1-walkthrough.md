# fpga-cpu m1 walkthrough

Checkout: the tree after this commit. Commands assume repo root. Needs Python 3 and Icarus Verilog (`iverilog`, `vvp` on `PATH`).

```bash
python3 -m unittest compiler.tests.test_fpga_cpu_m1 -v
```

Expected: `Ran 7 tests ... OK`

## FPGA-CPU-001 — HDL tree

```bash
python3 -m unittest compiler.tests.test_fpga_cpu_m1.TestFpgaCpuM1.test_FPGA_CPU_001
```

`emu/fpga-cpu/rtl/` contains at least one `.v` file.

## FPGA-CPU-002 — YAP1 load

```bash
python3 -m unittest compiler.tests.test_fpga_cpu_m1.TestFpgaCpuM1.test_FPGA_CPU_002
```

Halt YAP1: dumped `pc` is 0. SRAM word 0 is the halt encoding, not ASCII `YAP1`.

## FPGA-CPU-003 — halt vs cap

```bash
python3 -m compiler.asm /dev/stdin -o /tmp/halt.yap <<'EOF'
halt
EOF
python3 emu/fpga-cpu/sim.py /tmp/halt.yap; echo $?
```

Expected: dump includes `halted 1`; exit `0`.

A `nop`-only image with `--max-cycles 8` exits non-zero (see the unittest).

## FPGA-CPU-004 — Linux Icarus

```bash
python3 -m unittest compiler.tests.test_fpga_cpu_m1
```

Passes on this host with `iverilog`/`vvp`.

## FPGA-CPU-005 — multi-cycle halt

```bash
python3 -m unittest compiler.tests.test_fpga_cpu_m1.TestFpgaCpuM1.test_FPGA_CPU_005
```

Halt run cycle count `> 1`.

## FPGA-CPU-006 — ucode.hex

```bash
python3 -m unittest compiler.tests.test_fpga_cpu_m1.TestFpgaCpuM1.test_FPGA_CPU_006
```

Generated `ucode.hex` has 256 lines of 16 hex digits; line 1 matches `yap_cpu` fetch word 0.

## FPGA-CPU-012 — halt holds

```bash
python3 -m unittest compiler.tests.test_fpga_cpu_m1.TestFpgaCpuM1.test_FPGA_CPU_012
```

After halt, `pc` stays 0 and `ir` is the halt word (does not fetch a second insn).
