# physical-cpu m10 testplan

One acceptance check per claimed feature. Walkthrough commands are written by `/implement-m`.

| ID | Check |
|----|--------|
| PHYSICAL-CPU-015 | `hw/alu/` schematic text includes `a`, `b`, `y`, `op0`; spice instantiates `ADDER` and at least one of `AND`/`OR`/`XOR`. `ngspice -b`: ADD a=1 b=0 cin=0 → `y` VOH ≥ 3.0 V, `cout` VOL ≤ 0.3 V; SUB a=1 b=0 → `y` VOH; AND a=1 b=1 → `y` VOH; XOR a=1 b=1 → `y` VOL. |
