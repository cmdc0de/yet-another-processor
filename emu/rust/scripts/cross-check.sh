#!/bin/sh
# Typecheck every v1 host triple. Link Windows GNU tests when mingw is present.
set -e
root=$(CDPATH= cd -- "$(dirname "$0")/.." && pwd)
cd "$root"

rustup target add \
    aarch64-unknown-linux-gnu \
    x86_64-pc-windows-gnu \
    aarch64-pc-windows-msvc \
    aarch64-apple-darwin

for triple in \
    aarch64-unknown-linux-gnu \
    x86_64-pc-windows-gnu \
    aarch64-pc-windows-msvc \
    aarch64-apple-darwin
do
    echo "== cargo check --target $triple =="
    cargo check --target "$triple"
done

echo "== cargo test --no-run --target x86_64-pc-windows-gnu =="
cargo test --no-run --target x86_64-pc-windows-gnu

echo "cross-check: cargo check OK for 007–010; Windows GNU test binaries linked."
echo "Native: cargo test --manifest-path emu/rust/Cargo.toml on each host."
