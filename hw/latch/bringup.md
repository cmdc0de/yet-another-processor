# Latch bring-up (PHYSICAL-CPU-017)

Assemble `hw/latch/latch.kicad_pcb` from `bom.txt` and `assembly.md` (which MOSFET, which pin, which net). Header pin order **VDD, VSS, D, EN, Q** (2.54 mm).

Rails: VDD = 3.3 V, VSS = 0. Measure Q vs VSS. Same follow/hold as PHYSICAL-CPU-004.

| Name | Stimulus | Pass |
|------|----------|------|
| qfollow0 | EN=3.3, D=0 | Q ≤ 0.3 V |
| qfollow1 | EN=3.3, D=3.3 | Q ≥ 3.0 V |
| qhold1 | after qfollow1, set EN=0, then D=0 | Q ≥ 3.0 V |
| qhold0 | EN=3.3, D=0 until Q low; EN=0; then D=3.3 | Q ≤ 0.3 V |

Write those four voltages to `hw/latch/bench.txt`:

```
qfollow0 = <volts>
qfollow1 = <volts>
qhold1 = <volts>
qhold0 = <volts>
```
