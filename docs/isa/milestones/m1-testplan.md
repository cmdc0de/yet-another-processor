# ISA m1 testplan

One acceptance check per claimed feature. Walkthrough commands are written by `/implement-m`.

| ID | Check |
|----|--------|
| ISA-001 | A packed instruction is 4 bytes; an address `+4` stays in 32 bits (mod 2^32). |
| ISA-002 | All 32 names `r0`–`r31` index the same file; `r32` is rejected. |
| ISA-003 | After one R-type step, `PC` is old `PC+4`. |
| ISA-004 | `add t0, one, ones` sets N=1, Z=0; `add zero, zero, zero` sets Z=1, N=0. C/V match design.md on overflowing ADD and borrowing SUB. |
| ISA-005 | `add t0, one, one` → `t0==2`; encoding opcode=0, funct=ADD. |
| ISA-006 | `sub t0, one, one` → `t0==0`, Z=1. |
| ISA-007 | `and t0, ones, one` → `t0==1`. |
| ISA-008 | `or t0, zero, one` → `t0==1`. |
| ISA-009 | `xor t0, ones, ones` → `t0==0`. |
| ISA-010 | `not t0, zero` → `t0==0xFFFFFFFF`. |
| ISA-011 | `sll t0, one, 3` → `t0==8`. |
| ISA-014 | `add t0, one, one` then `cmp t0, one`: `t0` still 2; Z=0, C=0 (2≥1 unsigned), N=0. `cmp one, t0`: C=1 (borrow). Encoding funct=CMP. |
| ISA-031 | `nop` packs identically to `sll zero, zero, 0`; stepping it does not change GPRs. |
| ISA-050 | Assembler names `zero,one,ones,ra,sp,a0,fp,k0` map to r0,r1,r2,r3,r4,r5,r30,r31. |
| ISA-052 | `add t0, one, one` then `test t0, one`: `t0` still 2; Z=0, N=0, C=0, V=0. `test t0, zero`: Z=1. Odd: `test t0, one` then Z=0. Encoding funct=TEST. |
| ISA-053 | `add t0, one, one` then `teq t0, t0`: `t0` still 2; Z=1, N=C=V=0. `teq t0, one`: Z=0. Encoding funct=TEQ. |
| ISA-054 | `add zero, one, one` leaves `r0==0` and sets Z=0 (result would have been 2). |
| ISA-055 | After `add one, zero, ones`, `r1` is still 1. |
| ISA-056 | After `add ones, zero, zero`, `r2` is still `0xFFFFFFFF`. |
