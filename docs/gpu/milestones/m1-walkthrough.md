# gpu m1 walkthrough

Checkout: the tree after this commit. Commands assume repo root. Needs Python 3 and **Icarus Verilog** (`iverilog`, `vvp` on `PATH`).

```bash
python3 -m unittest compiler.tests.test_gpu_m1 -v
```

Expected: `Ran 6 tests ... OK`.

## GPU-001 — HDL tree

```bash
python3 -m unittest compiler.tests.test_gpu_m1.TestGpuM1.test_GPU_001
```

`gpu/` contains Verilog-2001 `.v` files.

## GPU-002 — sim runs

```bash
python3 -m unittest compiler.tests.test_gpu_m1.TestGpuM1.test_GPU_002
```

`iverilog` + `vvp` of the GPU sim exits 0 and writes a PPM.

## GPU-003 — Icarus required

```bash
python3 -m unittest compiler.tests.test_gpu_m1.TestGpuM1.test_GPU_003
```

Fails if `iverilog` or `vvp` is not on `PATH`.

## GPU-004 — GPU-local backbuffer

```bash
python3 -m unittest compiler.tests.test_gpu_m1.TestGpuM1.test_GPU_004
```

RTL stores pixels in a GPU-local `fb` array, not the CPU bus SRAM.

## GPU-005 — YAP-160 RGB888

```bash
python3 -m unittest compiler.tests.test_gpu_m1.TestGpuM1.test_GPU_005
```

Sources state 160×120 and RGB888 (`0x00RRGGBB` / P6).

## GPU-006 — black reset dump

```bash
python3 -m unittest compiler.tests.test_gpu_m1.TestGpuM1.test_GPU_006
```

PPM P6 is 160×120 and every pixel is `00 00 00` after reset.
