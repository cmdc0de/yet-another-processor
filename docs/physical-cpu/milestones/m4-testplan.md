# physical-cpu m4 testplan

One acceptance check per claimed feature. Walkthrough commands are written by `/implement-m`.

| ID | Check |
|----|--------|
| PHYSICAL-CPU-009 | `hw/reg32/` spice instantiates `LATCH` 32 times with one `WE` on every `EN`; `ngspice -b`: `WE`=1 D=0 then D=all-ones → every `q` at VOL then VOH; `WE`=0 D flipped → every `q` holds VOH. Schematic text includes `d0`, `d31`, `q0`, `q31`, `WE`. |
