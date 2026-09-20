# fpga-cpu m4

Features: FPGA-CPU-014, FPGA-CPU-015, FPGA-CPU-016

## Intent

COP1 moves and unimplemented-COP1 traps on the Icarus CPU, same as `compiler.yap_cpu`. ISA execute programs from `compiler.tests.test_m*` run as YAP1s on the sim and match `yap_cpu`. `os/kernel.s` reaches halt (sim exit 0), as on `yap-emu`. m1–m3 tests still pass.

## Work

- 32 COP1 `f` regs. DISPATCH: `mfc1`/`mtc1` to `U_MFC1`/`U_MTC1`; other COP1 → `U_COP_UNIMP` (CAUSE=6). `mfc1` writes `f[fs]` to `rd`; `mtc1` writes GPR to `f[fs]` (`we_csr` on the MTC1 word, as in `ucode.py`).
- Replay ISA execute cases from `compiler.tests.test_m*` as YAP1+halt (not a rewrite of those files; encoding-only tests stay on `yap_isa`). Compare sim dump to `yap_cpu`.
- Assemble `os/kernel.s` to YAP1; `python3 emu/fpga-cpu/sim.py` exits 0. Same default user path as OS m3 (write then `SYS_EXIT`).
- Tests in `compiler/tests/test_fpga_cpu_m4.py`.

## Done

- FPGA-CPU-014: same images as cpu m4 CPU-017, 031 (`mtc1`/`mfc1` round-trip; COP1 `rs` not MFC1/MTC1 → CAUSE=6)
- FPGA-CPU-015: ISA execute images from `test_m*` (at least one execute check per `test_m1`–`test_m6` that runs an insn) match `yap_cpu` on the sim
- FPGA-CPU-016: `os/kernel.s` YAP1; sim exit 0; halted

## Out of scope

Later-generation FPGA-CPU-017–020 (synthesis, board SRAM, caches, VM).
