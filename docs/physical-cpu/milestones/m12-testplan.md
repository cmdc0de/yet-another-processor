# physical-cpu m12 testplan

One acceptance check per claimed feature. Walkthrough commands are written by `/implement-m`.

| ID | Check |
|----|--------|
| PHYSICAL-CPU-017 | `hw/latch/` BOM (or equivalent text) names `IRLML6246`, `IRLML6401`, and the 2.54 mm header. `hw/latch/bench.txt` has `qfollow0` ≤ 0.3 V, `qfollow1` ≥ 3.0 V, `qhold1` ≥ 3.0 V, `qhold0` ≤ 0.3 V. m11 `.kicad_pcb` still parses. |
