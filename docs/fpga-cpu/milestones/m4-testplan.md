# fpga-cpu m4 testplan

One acceptance check per claimed feature. Walkthrough commands are written by `/implement-m`.

| ID | Check |
|----|--------|
| FPGA-CPU-014 | Same images as cpu m4 CPU-017, 031. Sim GPRs/CAUSE match `yap_cpu` |
| FPGA-CPU-015 | Execute images taken from `compiler.tests.test_m1`–`test_m6` (one per file that steps the CPU). Sim GPRs/FLAGS/CAUSE match `yap_cpu` |
| FPGA-CPU-016 | Assemble `os/kernel.s` to a YAP1; `python3 emu/fpga-cpu/sim.py <image>` exits 0 (`halted 1`) |
