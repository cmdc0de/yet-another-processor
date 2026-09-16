# ISA m2 testplan

One acceptance check per claimed feature, plus `sllv`. Walkthrough commands are written by `/implement-m`.

| ID | Check |
|----|--------|
| ISA-012 | `sll t0, one, 3` then `srl t0, t0, 2` → `t0==2`. `srlv t0, t0, one` → `t0==1`. funct=SRL / SRLV. |
| ISA-013 | `lui t0, 0x8000` → `0x80000000`. `sra t0, t0, 1` → `0xC0000000`, N=1. `srav t0, t0, one` → `0xE0000000`. funct=SRA / SRAV. |
| ISA-015 | `addi t0, one, -1` → `t0==0`, Z=1. `andi t0, ones, 0x00FF` → `0xFF` (zero-extend). `ori t0, zero, 1` → 1. `xori t0, ones, 0` → `0xFFFFFFFF`. |
| ISA-016 | `mul t0, one, ones` → `t0==0xFFFFFFFF` (low 32 of 1 × 0xFFFFFFFF). `mul t0, ones, ones` → `t0==1` (low 32 of 0xFFFFFFFF²). funct=MUL. Z set when low 32 is 0. |
| ISA-025 | `lui t0, 0x1234` → `0x12340000`. `ori t0, t0, 0x5678` → `0x12345678`. opcode=LUI. FLAGS unchanged by `lui`. |
| ISA-026 | `PC=0`, `adr t0, 16` → `t0==20` (`PC+4+16`). opcode=ADR. FLAGS unchanged. |
| sllv | `sllv t0, one, t1` with `t1==3` → `t0==8`. funct=SLLV. |
