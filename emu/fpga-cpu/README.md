# FPGA CPU (simulation)

Verilog-2001 + Icarus. See `docs/fpga-cpu/design.md`.

```bash
python3 emu/fpga-cpu/sim.py image.yap
python3 emu/fpga-cpu/sim.py image.yap --max-cycles 8
```

Needs `iverilog` and `vvp` on `PATH`. Microcode `ucode.hex` is generated from `compiler.yap_cpu` on each run.
