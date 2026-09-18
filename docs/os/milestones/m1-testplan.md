# os m1 testplan

One acceptance check per claimed feature. Walkthrough commands are written by `/implement-m`.

| ID | Check |
|----|--------|
| OS-001 | Assembled payload: bytes at `0x80` are a valid insn (e.g. `halt`); not required to equal the reset insn at 0. |
| OS-002 | `yap-emu os/kernel.yap` (or the test’s equivalent) exits 0. |
| OS-003 | After that run, dump has `sp`/`r4` == `0x1000`. |
| OS-018 | `python3 -m compiler.asm os/kernel.s -o …` exits 0. |
| OS-019 | Automated test: assemble from `os/` and run `yap-emu`; both succeed. |
