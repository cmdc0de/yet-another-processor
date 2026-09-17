# ISA m6 testplan

One acceptance check per claimed feature. Walkthrough commands are written by `/implement-m`.

| ID | Check |
|----|--------|
| ISA-043 | Packed `mfc1` opcode is COP1 (`010001`), not SPECIAL or COP0. |
| ISA-044 | `mtc1 t0, f0` then `mfc1 t1, f0` copies the value. `f0` is not a GPR. |
| ISA-045 | COP1 word with a non-move `rs`/funct traps CAUSE=6, PC=0x80. |
| ISA-046 | `parse_reg("sp")==4`; writing `sp` works; `zero`/`one`/`ones` still discard writes. |
| ISA-047 | Helper: `sp=0x200`, push two words → `sp==0x1F8`, `sp%8==0`, memory at the old slots holds the values, addresses decrease. |
| ISA-048 | `ra=3, a0=5, a3=8, s0=16, s11=27, fp=30, k0=31`. `k0` is not in the user C set used by the helper. |
