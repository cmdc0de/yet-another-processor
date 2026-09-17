# Assembler m4 testplan

One acceptance check per claimed feature. Walkthrough commands are written by `/implement-m`.

| ID | Check |
|----|--------|
| COMPILER-015 | `li t0, 1` payload is one word, `addi`. `li t0, 0x12345678` is two words; running them on `Cpu` leaves `t0==0x12345678`. |
| COMPILER-016 | `move t0, sp` equals `add t0, sp, zero`. |
| COMPILER-017 | `lab: nop` / `la t0, lab` uses `adr` (one word). `.org 0x20000` / `far:` / `la t0, far` from address 0 is two words (`lui`+`ori`) and `t0==0x20000` after step. |
| COMPILER-020 | `python3 -m compiler.asm halt.s -o h.yap --run` exits 0. A `j loop` / `loop: j loop` program `--run` exits non-zero. |
