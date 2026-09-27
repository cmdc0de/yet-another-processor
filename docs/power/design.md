# Power design (v1 + m2)

5 V in, 3.3 V CPU core through a regulator. Same **VDD** / **VSS** names as cells, bus, and MCU. Not MOSFET cells. Not 5 V I/O.

## Rails

| Knob | v1 / m2 |
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

## Regulator (v1)

Behavioral subckt **`REG33`**. Pins VIN, VDD, VSS. Always on. m2 keeps these pin names; the implementation is the named IC below.

## Regulator (m2)

Named LDO. `REG33` remains the sim pin names (VIN, VDD, VSS).

| Knob | m2 |
|------|----|
| Part | **AP2112M-3.3TRG1** (Diodes / BCD AP2112-3.3) |
| Package | **SOIC-8** (3.90 mm) |
| VOUT | fixed **3.3 V**, ±1.5% (still inside 3.20–3.40 V) |
| IOUT | 600 mA min |
| VIN max | 6 V (test still **5.0 V**) |
| Enable | **EN active-high**; tied to VIN (always on, same as v1) |
| PGOOD | **none** on this part |
| CIN / COUT | **1.0 µF** ceramic each (X5R/X7R), VIN–VSS and VDD–VSS |

### SOIC-8 pins (top view)

| Pin | Name | Net |
|-----|------|-----|
| 1 | VOUT | VDD |
| 2, 3, 4 | NC | no connect |
| 5 | EN | VIN (always on in m2); driven in m3 |
| 6, 7 | GND | VSS |
| 8 | VIN | VIN |

## Enable (m3)

AP2112M-3.3TRG1 **EN** is active-high. No PGOOD pin. CPU / bus / MCU 3.3 V is this **VDD**.

| EN vs VSS | VDD |
|-----------|-----|
| **≥ 1.5 V** (e.g. tied to VIN=5.0 V as in m2) | 3.20–3.40 V |
| **0 V** (off) | **≤ 0.3 V** after settling |

m2 rail test stays EN=VIN. m3 adds a netlist that drives EN.

## CAD

| Knob | v1 | m2 |
|------|----|----|
| Simulator | **ngspice** batch (`ngspice -b`) | same |
| Host | Linux, no GUI | same |
| Netlist | SPICE `.cir` / `.subckt` | same; sources name AP2112M-3.3TRG1 |
| Schematic | not required | KiCad **6** `.kicad_sch` (text parse, no `kicad-cli`) |

Missing `ngspice` fails tests (not skip).

## Tree

```
hw/power/
  *.subckt / .cir     REG33 + rail test
  *.kicad_sch         LDO schematic (m2)
```

Python unittest under `compiler/tests/` runs `ngspice -b` and reads printed `v(vdd)`.

## Out of this document

Fab vendor / gerber order, USB 5 V, FPGA/MCU board PGOOD handshake (this IC has no PGOOD), current budget, thermal, bench measurement, CELL-019 5 V I/O cells.
