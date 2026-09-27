# fpu m2 testplan

One acceptance check per claimed feature. Walkthrough commands are written by `/implement-m`.

Binary32: `1.0=0x3F800000`, `2.0=0x40000000`, `3.0=0x40400000`, `0.5=0x3F000000`, `6.0=0x40C00000`, `+inf=0x7F800000`.

| ID | Check |
|----|--------|
| FPU-006 | `f2=1.0`, `f3=2.0`, add (`funct=0`) into `f1` → `f1=0x40400000` |
| FPU-007 | `f2=1.0`, `f3=0.5`, sub (`funct=1`) into `f1` → `f1=0x3F000000` |
| FPU-008 | `f2=2.0`, `f3=3.0`, mul (`funct=2`) into `f1` → `f1=0x40C00000` |
| FPU-009 | `1.0÷2.0` → `0x3F000000`; `1.0÷0.0` → `0x7F800000`; `0.0÷0.0` → `0x7FC00000` |
