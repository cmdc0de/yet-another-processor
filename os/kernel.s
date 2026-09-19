; v1 kernel (os m2). Reset PC=0; trap at 0x80; user at 0x1000.
; SYS_EXIT (sys 1): save GPRs, halt, leave user sp (choice A).

.org 0
    li sp, 0x1000
    li t0, 0x1000
    mtc0 t0, ubase
    li t0, 0x8000
    mtc0 t0, ulimit
    li t0, 0x1000
    mtc0 t0, epc
    li t0, 2
    mtc0 t0, status
    li sp, 0x8000
    eret

.org 0x80
    move k0, sp
    li sp, 0x1000
    sw k0, -4(sp)
    sw a0, -8(sp)
    sw a1, -12(sp)
    sw a2, -16(sp)
    sw a3, -20(sp)
    sw a4, -24(sp)
    sw ra, -28(sp)
    mfc0 k0, cause
    addi k0, k0, -3
    teq k0, zero
    beq sys_ok
    lw sp, -4(sp)
    halt
sys_ok:
    mfc0 k0, epc
    addi k0, k0, -4
    lw k0, 0(k0)
    andi k0, k0, 0xFFFF
    addi k0, k0, -1
    teq k0, zero
    beq do_exit
    lw sp, -4(sp)
    halt
do_exit:
    lw sp, -4(sp)
    halt

.org 0x1000
    sys 1
