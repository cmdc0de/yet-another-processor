# Latch assembly (PHYSICAL-CPU-017)

Board: `hw/latch/latch.kicad_pcb`. BOM: `bom.txt`. Parts and nets below. Pads that share a net are tied by copper (front verticals, back buses, vias). Silkscreen `QN_*` / `QP_*` is the pick-and-place map.

## SOT-23 pinout (IRLML6246 and IRLML6401)

| Pin | Name |
|-----|------|
| 1 | Gate |
| 2 | Source |
| 3 | Drain |

`QN_*` = IRLML6246 (N). `QP_*` = IRLML6401 (P).

## Header J1 (2.54 mm)

Pin 1 (square) toward pin 5: **VDD, VSS, D, EN, Q**. That is the only connector you drive.

## MOSFET map

Same net name = one copper node.

| Ref | Part | Pin1 G | Pin2 S | Pin3 D |
|-----|------|--------|--------|--------|
| QN_EN | IRLML6246 | EN | VSS | ENB |
| QP_EN | IRLML6401 | EN | VDD | ENB |
| QN_ININV | IRLML6246 | EN | VSS | ENB_IN |
| QP_ININV | IRLML6401 | EN | VDD | ENB_IN |
| QN_IN1 | IRLML6246 | EN | D | MIDN_IN |
| QN_IN2 | IRLML6246 | EN | N1 | MIDN_IN |
| QP_IN1 | IRLML6401 | ENB_IN | D | MIDP_IN |
| QP_IN2 | IRLML6401 | ENB_IN | N1 | MIDP_IN |
| QN_I1 | IRLML6246 | N1 | VSS | QB |
| QP_I1 | IRLML6401 | N1 | VDD | QB |
| QN_I2 | IRLML6246 | QB | VSS | Q |
| QP_I2 | IRLML6401 | QB | VDD | Q |
| QN_FBINV | IRLML6246 | ENB | VSS | ENB_FB |
| QP_FBINV | IRLML6401 | ENB | VDD | ENB_FB |
| QN_FB1 | IRLML6246 | ENB | Q | MIDN_FB |
| QN_FB2 | IRLML6246 | ENB | N1 | MIDN_FB |
| QP_FB1 | IRLML6401 | ENB_FB | Q | MIDP_FB |
| QP_FB2 | IRLML6401 | ENB_FB | N1 | MIDP_FB |

Internal nets (do not bring out): ENB, ENB_IN, ENB_FB, N1, QB, MIDN_IN, MIDP_IN, MIDN_FB, MIDP_FB.
