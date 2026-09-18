# emu-rust m5 walkthrough

Checkout: the tree after this commit. Commands assume repo root. Rustc/cargo 1.74+ (tested with 1.98).

```bash
cargo test --manifest-path emu/rust/Cargo.toml
```

Expected: all tests `ok` (m1–m5).

m5 only:

```bash
cargo test --manifest-path emu/rust/Cargo.toml test_emu_rust_005 test_emu_rust_024 test_emu_rust_025 test_emu_rust_026 test_emu_rust_027 test_emu_rust_028 test_emu_rust_029 test_emu_rust_030 test_emu_rust_031 test_emu_rust_032 -- --exact
```

Expected: 10 passed (CLI `test_emu_rust_005` plus nine library tests).

## EMU-RUST-005 — dump

```bash
cargo test --manifest-path emu/rust/Cargo.toml --test cli test_emu_rust_005 -- --exact
```

`halt` YAP1 CLI stdout contains `pc`, `flags`, `cause`, and `r10`.

```bash
python3 -c "from compiler.asm import assemble_source; open('/tmp/halt.yap','wb').write(assemble_source('halt\n'))"
cargo run --manifest-path emu/rust/Cargo.toml -- /tmp/halt.yap
```

Stdout includes those names; exit 0.

## EMU-RUST-024 — privilege reset

```bash
cargo test --manifest-path emu/rust/Cargo.toml test_emu_rust_024 -- --exact
```

Reset: P=1, IE=0, PC=0. `mtc0` STATUS with P=0 → user.

## EMU-RUST-025 — MFC0/MTC0

```bash
cargo test --manifest-path emu/rust/Cargo.toml test_emu_rust_025 -- --exact
```

User `mtc0` UBASE → CAUSE=7. Supervisor `mtc0` UBASE succeeds. User `mfc0` FLAGS does not trap.

## EMU-RUST-026 — trap entry

```bash
cargo test --manifest-path emu/rust/Cargo.toml test_emu_rust_026 -- --exact
```

`sys 1` at PC=0: CAUSE=3, EPC=4, P=1, IE=0, PC=0x80.

## EMU-RUST-027 — ERET

```bash
cargo test --manifest-path emu/rust/Cargo.toml test_emu_rust_027 -- --exact
```

After that `sys`, `eret` → PC=4, P restored.

## EMU-RUST-028 — user window

```bash
cargo test --manifest-path emu/rust/Cargo.toml test_emu_rust_028 -- --exact
```

UBASE=0x100, ULIMIT=0x200, user `lw` at 0 → CAUSE=2; supervisor `lw` at 0 succeeds.

## EMU-RUST-029 — IRQ

```bash
cargo test --manifest-path emu/rust/Cargo.toml test_emu_rust_029 -- --exact
```

IE=0, `irq()` does not trap. IE=1, `irq()` traps CAUSE=1.

## EMU-RUST-030 — sys

```bash
cargo test --manifest-path emu/rust/Cargo.toml test_emu_rust_030 -- --exact
```

`sys` → CAUSE=3.

## EMU-RUST-031 — TE reserved

```bash
cargo test --manifest-path emu/rust/Cargo.toml test_emu_rust_031 -- --exact
```

Supervisor `mtc0` STATUS with TE=1 → CAUSE=7; TE stays 0.

## EMU-RUST-032 — reserved CAUSE 4/5

```bash
cargo test --manifest-path emu/rust/Cargo.toml test_emu_rust_032 -- --exact
```

Translation-miss=4, page-fault=5. A normal `add` does not set them.
