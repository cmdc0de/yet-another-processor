# physical-cpu m12

Features: PHYSICAL-CPU-017

## Intent

Assemble the m11 latch (SOT-23 MOSFETs + header) and bring it up at 3.3 V: follow and hold within cell VOL/VOH. Results live in-tree so tests do not need a live bench on the CI host.

## Work

- `hw/latch/`: BOM naming IRLML6246, IRLML6401, 2.54 mm header VDD VSS D EN Q; short bring-up notes.
- `hw/latch/bench.txt`: measured `qfollow0`, `qfollow1`, `qhold1`, `qhold0`.
- unittest `compiler/tests/test_physical_cpu_m12.py`; m11 PCB parse still green.

## Done

- PHYSICAL-CPU-017: BOM names those parts; bench file follow/hold voltages sit in VOL ≤ 0.3 V / VOH ≥ 3.0 V

## Out of scope

PHYSICAL-CPU-018–020. Gerber/fab vendor. Adder PCB. Live DMM in unittest (file is the evidence).
