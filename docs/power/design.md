# Power design (v1)

5 V in, 3.3 V CPU core through a regulator. Same **VDD** / **VSS** names as cells, bus, and MCU. Not MOSFET cells. Not a named regulator IC. Not 5 V I/O.

## Rails

| Knob | v1 |
|------|----|
| VIN | **5.0 V** system input (net **VIN**) |
| VDD | **3.3 V** CPU core (net **VDD**) |
| VSS | **0 V** (net **VSS**, SPICE node 0) |
| Test VIN | DC **5.0 V** VIN to VSS |
| Test load | **1 kΩ** VDD to VSS |
| VDD window | **3.20 V ≤ VDD ≤ 3.40 V** after settling |

VIN is only the board input. VDD is the 3.3 V rail. Do not alias VIN as VDD.

## Domain

These sit on **VDD**, not VIN:

- CPU core (cells / physical CPU)
- SRAM and bus (`docs/memory-bus/design.md`)
- MCU I/O (`docs/mcu/design.md`)

v1 has no 5 V I/O net. Level shifters are POWER-009 (later).

## Regulator

Behavioral subckt **`REG33`**. Not a vendor part (POWER-008 later).

| Pin | Net |
|-----|-----|
| VIN | 5 V input |
| VDD | 3.3 V output |
| VSS | return |

Always on. No enable, no PGOOD (POWER-010 later). When the test source puts 5.0 V on VIN, VDD is inside the window above.

## CAD

| Knob | v1 |
|------|----|
| Simulator | **ngspice** batch (`ngspice -b`) |
| Host | Linux, no GUI |
| Netlist | SPICE `.cir` / `.subckt` |
| KiCad / LTspice GUI | not required for tests |

Missing `ngspice` fails tests (not skip).

## Tree

```
hw/power/
  *.subckt / .cir     REG33 + rail test
```

Python unittest under `compiler/tests/` runs `ngspice -b` and reads printed `v(vdd)`.

## Out of this document

Regulator vendor/part, PCB, USB 5 V, enable/PGOOD, current budget, thermal, bench measurement, CELL-019 5 V I/O cells.
