# fpga-cpu m4 walkthrough

Checkout: the tree after this commit. Commands assume repo root. Needs Python 3 and Icarus Verilog (`iverilog`, `vvp` on `PATH`).

```bash
python3 -m unittest compiler.tests.test_fpga_cpu_m4 compiler.tests.test_fpga_cpu_m3 compiler.tests.test_fpga_cpu_m2 compiler.tests.test_fpga_cpu_m1 -v
```

Expected: `Ran 16 tests ... OK`. m1–m3 still pass.

## FPGA-CPU-014 — COP1 moves and trap

```bash
python3 -m unittest compiler.tests.test_fpga_cpu_m4.TestFpgaCpuM4.test_FPGA_CPU_014
```

Same images as cpu m4 CPU-017, 031. `mtc1`/`mfc1` round-trip; unimplemented COP1 → CAUSE=6. Sim GPRs/CAUSE match `yap_cpu`.

## FPGA-CPU-015 — ISA execute images

```bash
python3 -m unittest compiler.tests.test_fpga_cpu_m4.TestFpgaCpuM4.test_FPGA_CPU_015
```

Execute images from `test_m1`–`test_m6` (add, sll, div, beq, sys, mfc1/mtc1). Sim GPRs/FLAGS/CAUSE match `yap_cpu`.

## FPGA-CPU-016 — kernel halt

```bash
python3 -m compiler.asm os/kernel.s -o /tmp/kernel.yap
python3 emu/fpga-cpu/sim.py /tmp/kernel.yap; echo $?
```

Expected: dump includes `halted 1`; exit `0`.
