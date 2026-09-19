# cpu m2 testplan

One acceptance check per claimed feature. Walkthrough commands are written by `/implement-m`.

| ID | Check |
|----|--------|
| CPU-008 | `and t0, ones, one` → 1, `Z=0`; `xor t0, one, one` → 0, `Z=1`; `C=V=0` |
| CPU-009 | `sll t0, one, 1` → 2; C is the bit shifted out (`0` for this). `sra` of `ones` stays negative |
| CPU-010 | `cmp one, one` → `Z=1`, `t0` unchanged if present; `test one, zero` → `Z=1` |
| CPU-011 | `mul t0, one, one` → 1; `div t0, one, zero` → `t0==0`, `Z=1` |
| CPU-012 | `addi t0, one, -1` → 0, `Z=1`; `andi t0, ones, 0xFF` → `0xFF`; `lui t0, 1` → `0x10000` |
| CPU-013 | `adr t0, 4` at `PC=0` then halt → `t0==8` |
| CPU-032 | Two images: `add t0, t0, one; halt` vs `add s0, s0, one; halt`. Cycle count for the `s0` image is greater |
