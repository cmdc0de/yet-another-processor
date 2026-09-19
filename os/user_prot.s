; OS-006: user load at address 0 (CAUSE=2).
.org 0x1000
    lw t0, 0(zero)
    sys 1
