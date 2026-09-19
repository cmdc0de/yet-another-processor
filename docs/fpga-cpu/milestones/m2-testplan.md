# fpga-cpu m2 testplan

One acceptance check per claimed feature. Walkthrough commands are written by `/implement-m`.

| ID | Check |
|----|--------|
| FPGA-CPU-007 | Two YAP1s as in cpu m2 CPU-032. Sim cycle count for the `s0` image is greater |
| FPGA-CPU-008 | `add t0, one, one; halt`. Sim dump `pc`, `flags`, `r10` equal `yap_cpu` after `run()` |
| FPGA-CPU-009 | Same images as cpu m2 CPU-008, 009, 011, 012, 013 (and/xor, sll, mul/div, addi/andi/lui, adr). Sim GPRs/FLAGS match `yap_cpu` |
