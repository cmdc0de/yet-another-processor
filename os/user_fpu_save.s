; FPU-011: user f0 survives SYS_WRITE after kernel dirties f0.
.org 0x1000
    li t0, 0xA5A5A5A5
    mtc1 t0, f0
    la a0, msg
    li a1, 3
    sys 2
    mfc1 t1, f0
    sys 1
msg:
    .byte 0x79 0x61 0x70
