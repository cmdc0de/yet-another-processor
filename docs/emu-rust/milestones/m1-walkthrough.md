# emu-rust m1 walkthrough

Checkout: the tree after this commit. Commands assume repo root. Rustc/cargo 1.74+ (tested with 1.98). Linux x86_64.

```bash
cargo test --manifest-path emu/rust/Cargo.toml
```

Expected: all tests `ok` (library + `tests/cli.rs`).

## EMU-RUST-001 — CLI path

```bash
cargo test --manifest-path emu/rust/Cargo.toml --test cli test_emu_rust_001 -- --exact
```

No image path exits non-zero. A valid `halt` YAP1 path exits 0.

CLI smoke:

```bash
python3 -c "from compiler.asm import assemble_source; open('/tmp/halt.yap','wb').write(assemble_source('halt\n'))"
cargo run --manifest-path emu/rust/Cargo.toml -- /tmp/halt.yap
echo $?
```

Expected: `0`. `cargo run` with no image path is non-zero.

## EMU-RUST-002 — bad YAP1

```bash
cargo test --manifest-path emu/rust/Cargo.toml --test cli test_emu_rust_002 -- --exact
```

Shorter than 16 bytes, magic not `YAP1`, and `size != file_len-16` each exit non-zero.

## EMU-RUST-003 — load payload, skip header

```bash
cargo test --manifest-path emu/rust/Cargo.toml test_emu_rust_003 -- --exact
```

`load=0`, `entry=0`, payload = `halt` word: SRAM `[0,4)` is that word, not ASCII `YAP1`.

## EMU-RUST-004 — halt vs step cap

```bash
cargo test --manifest-path emu/rust/Cargo.toml --test cli test_emu_rust_004 -- --exact
```

`halt` YAP1 exits 0. Four zero words and `--max-steps 10` exits non-zero.

```bash
python3 -c "from compiler.asm import assemble_source; open('/tmp/zeros.yap','wb').write(assemble_source('nop\nnop\nnop\nnop\n'))"
cargo run --manifest-path emu/rust/Cargo.toml -- /tmp/zeros.yap --max-steps 10
echo $?
```

Expected: non-zero (`nop` is not implemented in m1, so it never halts).

## EMU-RUST-006 — Linux x86_64

```bash
uname -m
cargo test --manifest-path emu/rust/Cargo.toml
```

`uname -m` is `x86_64`. `cargo test` is OK.

## EMU-RUST-011 — little-endian SRAM

```bash
cargo test --manifest-path emu/rust/Cargo.toml test_emu_rust_011 -- --exact
```

Word `0x12345678` in SRAM is bytes `78 56 34 12`.

## EMU-RUST-023 — halt

```bash
cargo test --manifest-path emu/rust/Cargo.toml test_emu_rust_023 -- --exact
```

Step `halt`: halted is true. A second step leaves PC unchanged.
