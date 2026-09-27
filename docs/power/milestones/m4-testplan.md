# power m4 testplan

One acceptance check per claimed feature. Walkthrough commands are written by `/implement-m`.

| ID | Check |
|----|--------|
| POWER-009 | Sources name IO5, IO33, `LVLSH`. `ngspice -b`: HV=5.0 → LV in 3.20–3.40 V; LV=3.3 → HV in 4.75–5.25 V. m1–m3 still pass. |
