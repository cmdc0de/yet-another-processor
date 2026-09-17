# emu-rust m1 testplan

One acceptance check per claimed feature. Walkthrough commands are written by `/implement-m`.

| ID | Check |
|----|--------|
| EMU-RUST-001 | CLI with no image path exits non-zero. With a valid `halt` YAP1 path, it runs. |
| EMU-RUST-002 | File shorter than 16 bytes, magic not `YAP1`, or `size != file_len-16` each exit non-zero. |
| EMU-RUST-003 | Image with `load=0`, `entry=0`, payload = `halt` word: SRAM `[0,4)` is that word, not the ASCII header. |
| EMU-RUST-004 | `halt` YAP1 exits 0. Four zero words and `--max-steps 10` exits non-zero. |
| EMU-RUST-006 | `cargo test` (crate in `emu/rust/`) on Linux x86_64 is OK. |
| EMU-RUST-011 | After load, bytes at the payload address for `0x12345678` are `78 56 34 12`. |
| EMU-RUST-023 | Step `halt`; halted is true. A second step leaves PC unchanged (still halted). |
