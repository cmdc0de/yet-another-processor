# cells m3 testplan

One acceptance check per claimed feature. Walkthrough commands are written by `/implement-m`.

| ID | Check |
|----|--------|
| CELL-012 | Adder 8 input rows; `sum` and `cout` meet VOL/VOH for the boolean full-adder table |
| CELL-013 | EN=1, D=0 then D=3.3: Q at VOL then VOH |
| CELL-015 | Files `inverter_test.cir` … `mux2_test.cir`, `latch_test.cir`, `adder_test.cir` exist and `.include` / instantiate the matching `.subckt` |
| CELL-016 | `.tran`: load Q=1, EN=0, D→0; Q stays ≥ 3.0 V. Load Q=0, EN=0, D→3.3; Q stays ≤ 0.3 V |
| CELL-017 | a=b=cin=0 → sum ≤ 0.3 V, cout ≤ 0.3 V; a=b=cin=3.3 → sum ≥ 3.0 V, cout ≥ 3.0 V |
