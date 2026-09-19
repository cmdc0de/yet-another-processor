; OS-016: unknown sys then SYS_EXIT. Store a4 at 0x1100.
.org 0x1000
    sys 99
    li t0, 0x1100
    sw a4, 0(t0)
    sys 1
.org 0x1100
    .word 0
