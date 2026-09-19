# cpu m2

Features: CPU-008, CPU-009, CPU-010, CPU-011, CPU-012, CPU-013, CPU-032

## Intent

Finish integer execute on the clocked model. SPECIAL logic/shifts/compares/mul/div, I-type `addi`/`andi`/`ori`/`xori`/`lui`, and `ADR` retire with ISA flags. MOSFET-bank vs IC-bank reads take different cycle counts. m1 tests still pass.

## Work

- Microcode entries for `and`/`or`/`xor`/`not`, `sll`/`srl`/`sra` and `sllv`/`srlv`/`srav`, `cmp`/`test`/`teq`, `mul`/`div`, `addi`/`andi`/`ori`/`xori`/`lui`/`adr`.
- Flags per `docs/isa/design.md` (already in `flag_mode`). `LUI`/`ADR` do not write FLAGS. DIV ÷0 → `rd=0`, `Z=1`.
- Dispatch those opcodes/functs; unknown still TRAP 7.
- CPU-032: same insn with `t0` (MOSFET) vs `s0` (IC) as a source; IC path uses more cycles (`LAT_IC=2` vs `LAT_MOSFET=1`).
- Tests in `compiler/tests/test_cpu_m2.py`. m1 still passes.

## Done

- CPU-008: `and`/`or`/`xor`/`not` results and `Z N`; `C=V=0`
- CPU-009: `sll`/`srl`/`sra` (and register-shift forms); C=last bit out; `V=0`
- CPU-010: `cmp`/`test`/`teq` set flags and do not write a GPR
- CPU-011: `mul` low 32; `div` by 1 and by 0 (`rd=0`, `Z=1`)
- CPU-012: `addi` sign-extends; `andi` zero-extends; `lui` is `imm16<<16`
- CPU-013: `adr t0, 4` from `PC=0` → `t0==(PC+4)+4==8`
- CPU-032: `add t0, t0, one` uses fewer cycles than `add s0, s0, one` (same image shape)

## Out of scope

CPU-014–017 (loads, memory port as a feature, CSR/COP1 files), CPU-020, CPU-024–031, later-generation CPU-033–038.
