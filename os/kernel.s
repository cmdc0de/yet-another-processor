; v1 kernel boot (os m1). Reset PC=0; trap stub at 0x80.
; Kernel stack empty at 0x1000 (docs/os/design.md).

.org 0
    li sp, 0x1000
    halt

.org 0x80
    halt
