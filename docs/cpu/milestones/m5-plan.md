# cpu m5

Features: CPU-039, CPU-040, CPU-041, CPU-042, CPU-043

## Intent

Control transfer on the clocked model, same encodings as `docs/isa/design.md`. Taken jump/branch sets `PC` to the target (does not also add 4). Link writes `PC+4` of the jump. m1–m4 tests still pass.

## Work

- Microcode + dispatch for `j` (`a_sel=J-target`, `we_pc`), `jal` (write `ra` then same), `jr` (`PC←rs`), `jalr` (`rd←PC+4`, `PC←rs`), `bcc` (`PC+4+(sext(imm22)<<2)` if cond).
- Cond table is ISA Bcc (EQ/NE/LT/GE/LO/HS/LE/GT/MI/PL). Not taken: usual `PC+4` then fetch.
- Halt at jump/branch targets so tests stop. Tests in `compiler/tests/test_cpu_m5.py`.

## Done

- CPU-039: `j 0x20` from 0, halt at `0x20` → halted `PC==0x20`
- CPU-040: `jal 0x20` from 0, halt at `0x20` → `ra==4`, `PC==0x20`
- CPU-041: `addi t0, zero, 0x20`; `jr t0`; halt at `0x20` → `PC==0x20`
- CPU-042: `addi t0, zero, 0x20`; `jalr t1, t0`; halt at `0x20` → `t1==8`, `PC==0x20`
- CPU-043: `cmp one, one`; `beq 0x20` → `PC==0x20`. `cmp one, zero`; `beq 0x20`; halt → `PC==8`. `cmp zero, one`; `blo 0x20` taken; `bhs 0x20` not taken

## Out of scope

Later-generation CPU-033–038.
