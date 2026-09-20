# fpga-cpu m3 testplan

One acceptance check per claimed feature. Walkthrough commands are written by `/implement-m`.

| ID | Check |
|----|--------|
| FPGA-CPU-010 | Same images as cpu m3 CPU-014, 015, 026, 027. Sim GPRs/FLAGS/CAUSE (and SRAM at 0 for the LE store) match `yap_cpu` |
| FPGA-CPU-011 | Same images as cpu m5 CPU-039–043. Sim `pc` / link GPR match `yap_cpu` after halt |
| FPGA-CPU-013 | Same images as cpu m4 CPU-016, 020, 024, 025, 028, 029, 030 (not COP1). Sim CSRs/GPRs/`pc` match `yap_cpu` |
