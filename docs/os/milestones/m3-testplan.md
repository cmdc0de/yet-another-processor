# os m3 testplan

One acceptance check per claimed feature. Walkthrough commands are written by `/implement-m`.

| ID | Check |
|----|--------|
| OS-015 | Default image: SRAM `0x0800` is `YLOG`; `len` equals the user string length; bytes at `0x0808` match. `yap-emu` exits 0. |
| OS-016 | Fixture: `sys 99`, `sw a4` into user RAM, `sys 1`. That word is ≠ 0. Exit 0. |
| OS-017 | Fixture: `sys 2` with `a0=0`; log `len` still 0 (or unchanged); then `sys 1` exits 0. |
| OS-006 | Fixture: user `lw t0, 0(zero)` then would-be `sys 1`. Image still halts (exit 0). |
| OS-011 | Fixture: unaligned `lw` in user. Halt, exit 0. |
| OS-012 | Fixture: COP1 non-move from user. Log magic `KPAN` (`4B 50 41 4E`). Halt. |
