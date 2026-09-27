# power m3

Features: POWER-010

## Intent

Drive AP2112 **EN**. EN=VIN → VDD in window (m2). EN=0 → VDD off (≤ 0.3 V). m1–m2 tests still pass (default EN to VIN). ngspice `-b`.

## Work

- `hw/power/`: EN as a source in a dedicated test netlist (m2 rail test stays EN=VIN).
- unittest `compiler/tests/test_power_m3.py`; m1–m2 still green.

## Done

- POWER-010: EN high → VDD in 3.20–3.40 V; EN low → VDD ≤ 0.3 V

## Out of scope

POWER-009, POWER-011. No PGOOD net. No FPGA/MCU board bring-up.
