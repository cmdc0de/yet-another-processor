# physical-cpu m3 testplan

One acceptance check per claimed feature. Walkthrough commands are written by `/implement-m`.

| ID | Check |
|----|--------|
| PHYSICAL-CPU-008 | `hw/adder32/` spice instantiates `ADDER` 32 times with bit-*i* cout → bit-*i*+1 cin; `ngspice -b`: (1) a=b=cin=0 → every `sum` and `cout` at VOL; (2) a=all-ones, b=0, cin=1 → every `sum` at VOL and `cout` at VOH. Schematic text includes `a0`, `a31`, `sum0`, `sum31`. |
