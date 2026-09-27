# power m2

Features: POWER-008

## Intent

Replace the anonymous behavioral LDO with **AP2112M-3.3TRG1** on a KiCad schematic: VIN=5.0 V, EN to VIN, 1 µF CIN/COUT, VDD in 3.20–3.40 V with the 1 kΩ load. m1 rail tests still pass. ngspice `-b`.

## Work

- `hw/power/`: KiCad 6 schematic of the LDO; ngspice netlist instantiates the named part (or `REG33` that is that part).
- unittest `compiler/tests/test_power_m2.py`; m1 still green.

## Done

- POWER-008: sources name **AP2112M-3.3TRG1**; schematic has VIN, VOUT/VDD, GND/VSS, EN; sim `v(vdd)` still in 3.20–3.40 V

## Out of scope

POWER-009–011. No gerber/fab vendor. No USB. No PGOOD pin (this IC has none).
