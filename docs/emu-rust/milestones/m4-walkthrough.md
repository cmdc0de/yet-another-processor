# emu-rust m4 walkthrough

Checkout: the tree after this commit. Commands assume repo root. Rustc/cargo 1.74+ (tested with 1.98).

```bash
cargo test --manifest-path emu/rust/Cargo.toml
```

Expected: all tests `ok` (m1–m4).

m4 only:

```bash
cargo test --manifest-path emu/rust/Cargo.toml test_emu_rust_012 test_emu_rust_020 test_emu_rust_021 test_emu_rust_022 -- --exact
```

Expected: 4 passed.

## EMU-RUST-012 — fetch

```bash
cargo test --manifest-path emu/rust/Cargo.toml test_emu_rust_012 -- --exact
```

`add` at PC=0 → PC==4. Step with `PC=1` → CAUSE=8 and PC==0x80.

## EMU-RUST-020 — load/store

```bash
cargo test --manifest-path emu/rust/Cargo.toml test_emu_rust_020 -- --exact
```

`lw` of `78 56 34 12` → `0x12345678`. `sw` writes those bytes. `lb` of `0xFF` → `0xFFFFFFFF`; `lbu` → `0xFF`. `lh`/`lhu`/`sb`/`sh` as ISA. Unaligned `lw` at 1 → CAUSE=8.

## EMU-RUST-021 — jumps

```bash
cargo test --manifest-path emu/rust/Cargo.toml test_emu_rust_021 -- --exact
```

`j 0x20` → PC==0x20. `jal 0x20` → `ra==4`, PC==0x20. `jr ra` → PC==4. `jalr t0, t1` with t1==0x40 → t0==4, PC==0x40.

## EMU-RUST-022 — branches

```bash
cargo test --manifest-path emu/rust/Cargo.toml test_emu_rust_022 -- --exact
```

`cmp one, one` / `beq 0x20` taken. `cmp one, zero` / `beq 0x20` not taken (PC==8). `test one, one` / `bne 0x20` taken. `cmp zero, one` / `blo 0x20` taken.
