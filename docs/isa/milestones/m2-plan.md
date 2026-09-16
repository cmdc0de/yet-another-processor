# ISA m2

Features: ISA-012, ISA-013, ISA-015, ISA-016, ISA-025, ISA-026

Also implement: `sllv` (design.md register form of left shift; ISA-011 stays `done` from m1).

## Intent

Finish integer shifts (logical/arithmetic, shamt and register), I-type ALU immediates, `LUI`+`ORI` for 32-bit constants, `ADR` for PC-relative addresses, and `MUL` (low 32 bits).

## Work

- Pack/unpack I-type (`addi`/`andi`/`ori`/`xori`/`lui`/`adr`).
- SPECIAL `srl`/`sra`/`sllv`/`srlv`/`srav`/`mul`.
- Behavioral step; flags per `docs/isa/design.md`:
  - shifts: Z N, C=last bit shifted out, V=0
  - `ADDI`: Z N C V like ADD
  - `ANDI`/`ORI`/`XORI`: Z N, C=V=0
  - `LUI`/`ADR`: do not change FLAGS
  - `MUL`: Z N on low 32; C=V=0
- `ADDI` sign-extends; logical immediates zero-extend. No `SUBI`.
- `ADR`: `rd <- (PC+4) + sext(imm16)` (byte offset).
- `MUL`: `rd = low 32 of rs * rt` (32×32 → 64, take low).
- Tests in `m2-testplan.md`. m1 tests still pass.

## Done

- ISA-012: `srl` / `srlv` match encodings and results
- ISA-013: `sra` / `srav` match encodings and results (sign fill)
- ISA-015: `addi`/`andi`/`ori`/`xori` match encodings, extension, results
- ISA-016: `mul rd, rs, rt` writes low 32; encoding funct=MUL
- ISA-025: `lui` + `ori` forms an arbitrary 32-bit constant
- ISA-026: `adr rd, imm` is `(PC+4)+sext(imm16)`
- `sllv rd, rs, rt`: `rd = rs << rt[4:0]`

## Out of scope

DIV, load/store, jumps/branches, HALT, privilege, syscalls, coprocessor, ISA-051. Do not un-done ISA-011.
