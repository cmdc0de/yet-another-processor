# cells m1 testplan

One acceptance check per claimed feature. Walkthrough commands are written by `/implement-m`.

| ID | Check |
|----|--------|
| CELL-001 | Inverter (and NAND) test netlist includes a 3.3 V VDD source and 0 V ground |
| CELL-002 | `ngspice` log / netlist `.model` names include IRLML6246 and IRLML6401 |
| CELL-004 | Inverter: Vin=0 → Vout ≥ 3.0 V; Vin=3.3 → Vout ≤ 0.3 V |
| CELL-005 | NAND: AB=00,01,10 → Y ≥ 3.0 V; AB=11 → Y ≤ 0.3 V |
| CELL-014 | Same settled points as CELL-004/005 (VOL/VOH) |
| CELL-018 | Unittest invokes `ngspice -b`; no LTspice/GUI. Missing binary → test failure |
