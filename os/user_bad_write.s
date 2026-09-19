; OS-017: SYS_WRITE ptr 0 (outside window), then SYS_EXIT.
.org 0x1000
    move a0, zero
    li a1, 4
    sys 2
    sys 1
