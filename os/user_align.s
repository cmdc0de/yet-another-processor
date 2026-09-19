; OS-011: unaligned user lw (CAUSE=8).
.org 0x1000
    li t0, 0x1001
    lw t1, 0(t0)
    sys 1
