# gpu m2 walkthrough

Checkout: the tree after this commit. Commands assume repo root. Needs Python 3 and **Icarus Verilog** (`iverilog`, `vvp` on `PATH`).

```bash
python3 -m unittest compiler.tests.test_gpu_m2 compiler.tests.test_gpu_m1 -v
```

Expected: `Ran 8 tests ... OK`. m1 still passes.

## GPU-007 — MMIO port

```bash
python3 -m unittest compiler.tests.test_gpu_m2.TestGpuM2.test_GPU_007
```

RTL accepts writes at offsets `0x00`–`0x14` (CMD, COLOR, X0, Y0, X1, Y1).

## GPU-008 — rectangle fill

```bash
python3 -m unittest compiler.tests.test_gpu_m2.TestGpuM2.test_GPU_008
```

Fill COLOR=`0x00FF0000`, X0=0, Y0=0, X1=8, Y1=8: PPM pixels in that rect are `FF 00 00`; (8,0) and (0,8) stay `00 00 00`.
