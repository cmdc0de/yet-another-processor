# fpga-cpu m1 testplan

One acceptance check per claimed feature. Walkthrough commands are written by `/implement-m`.

| ID | Check |
|----|--------|
| FPGA-CPU-001 | `emu/fpga-cpu/rtl/` contains at least one `.v` file |
| FPGA-CPU-002 | Assemble `halt` to YAP1; after sim, dumped `pc` is 0 (entry). File magic `YAP1` is not SRAM[0:4] (SRAM[0:4] is the halt word) |
| FPGA-CPU-003 | `python3 emu/fpga-cpu/sim.py halt.yap` exits 0. Same driver on a 4-byte `nop` image with `--max-cycles 8` exits ≠ 0 |
| FPGA-CPU-004 | `python3 -m unittest compiler.tests.test_fpga_cpu_m1` (or the path we write) passes on this host |
| FPGA-CPU-005 | halt run prints or records a cycle count `> 1` |
| FPGA-CPU-006 | generated `ucode.hex` line 1 equals `{pack_cw(fetch0):016x}` from `yap_cpu` |
| FPGA-CPU-012 | halt image: dump `pc` stable; a second sim step/cap does not fetch a second insn (still halted) |
