; OS-012: unimplemented COP1 (rs != MFC1/MTC1) → CAUSE=6.
.org 0x1000
    .word 0x44100000
    sys 1
