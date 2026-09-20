# gpu m2 testplan

One acceptance check per claimed feature. Walkthrough commands are written by `/implement-m`.

| ID | Check |
|----|--------|
| GPU-007 | RTL/sim accepts writes at offsets `0x00`–`0x14` (CMD, COLOR, X0, Y0, X1, Y1) |
| GPU-008 | After fill COLOR=`0x00FF0000`, X0=0, Y0=0, X1=8, Y1=8: PPM pixels in that rect are `FF 00 00`; a pixel outside (e.g. 8,0 or 0,8) is still `00 00 00` |
