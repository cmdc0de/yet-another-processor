# power m1

Features: POWER-001, POWER-002, POWER-003, POWER-004, POWER-005, POWER-006, POWER-007

## Intent

ngspice in `hw/power/`: behavioral `REG33` from VIN=5.0 V to VDD. After settling, VDD is inside 3.20–3.40 V with the 1 kΩ load. CPU core, SRAM/bus, and MCU I/O use VDD, not VIN. Missing `ngspice` fails tests.

## Work

- `hw/power/`: `REG33` subckt + rail test `.cir`.
- unittest `compiler/tests/test_power_m1.py` runs `ngspice -b` and reads `v(vdd)`.

## Done

- POWER-001: sources under `hw/power/`
- POWER-002: sim builds and runs on Linux
- POWER-003: missing ngspice fails (not skip)
- POWER-004: named VIN (5.0 V) and VSS (0 V)
- POWER-005: `REG33` from VIN to VDD
- POWER-006: with 5 V in, `v(vdd)` is in 3.20–3.40 V
- POWER-007: CPU/bus/MCU documented on VDD, not VIN

## Out of scope

Later-generation 008–011. No named regulator IC. No PGOOD. No 5 V I/O.
