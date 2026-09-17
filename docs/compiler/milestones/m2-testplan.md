# Assembler m2 testplan

One acceptance check per claimed feature. Walkthrough commands are written by `/implement-m`.

| ID | Check |
|----|--------|
| COMPILER-008 | `loop: nop` then `j loop` — the `nop` is at address 0; symbol `loop==0`. |
| COMPILER-009 | `nop` / `loop: nop` / `j loop` — `j` target is 4. `beq loop` after `cmp one, one` at 0 encodes a taken branch to the label. |
| COMPILER-010 | `j loop` then `loop: halt` — `j` at 0 targets 4; payload is `j` then `halt`. |
| COMPILER-011 | `.org 0x80` / `halt` — `size>=0x84`; payload `[0x80:0x84]` is `halt`; `[0:0x80]` is zeros. `.org 4` after two `nop`s (LC already 8) is an error. |
