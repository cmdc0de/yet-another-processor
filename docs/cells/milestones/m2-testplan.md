# cells m2 testplan

One acceptance check per claimed feature. Walkthrough commands are written by `/implement-m`.

| ID | Check |
|----|--------|
| CELL-006 | NOR: AB=00 → Y ≥ 3.0 V; 01/10/11 → Y ≤ 0.3 V |
| CELL-007 | AND: AB=11 → Y ≥ 3.0 V; 00/01/10 → Y ≤ 0.3 V |
| CELL-008 | OR: AB=00 → Y ≤ 0.3 V; 01/10/11 → Y ≥ 3.0 V |
| CELL-009 | XOR: AB=01/10 → Y ≥ 3.0 V; 00/11 → Y ≤ 0.3 V |
| CELL-010 | TG EN=1, IN=0 and IN=3.3: OUT meets VOL/VOH. EN=0: OUT does not follow a 0→3.3 step on IN within the same DC op (hold/Hi-Z vs follow) |
| CELL-011 | Mux: S=0 Y=A; S=1 Y=B for A/B in {0, 3.3}, VOL/VOH |
