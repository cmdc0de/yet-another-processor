# emu-rust m2 testplan

One acceptance check per claimed feature. Walkthrough commands are written by `/implement-m`.

| ID | Check |
|----|--------|
| EMU-RUST-013 | Read `r0`==0, `r1`==1, `r2`==`0xFFFFFFFF`. `add t0, one, one` leaves `t0==2`. Write `r0` discarded; `add zero, one, one` still sets flags (Z=0). |
| EMU-RUST-014 | `add t0, one, ones` wraps to 0, Z=1, C=1. `sub t0, zero, one` → `t0==0xFFFFFFFF`, N=1, C=1 (borrow). |
| EMU-RUST-015 | `nop` encoding is `sll zero, zero, 0`. `and`/`or`/`xor`/`not`/`sll`/`cmp`/`test`/`teq` match `yap_isa.Cpu` on the same words (at least one check each). |
