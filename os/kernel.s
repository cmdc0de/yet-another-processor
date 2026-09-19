; v1 kernel (os m3). Reset PC=0; trap at 0x80; user at 0x1000.
; SYS_WRITE (sys 2) then SYS_EXIT (sys 1). Choice A: EXIT keeps user sp.

.equ LOG, 0x800
.equ LOG_LEN, 0x804
.equ LOG_CAP, 248

.org 0
    li sp, 0x1000
    li t0, 0x1000
    mtc0 t0, ubase
    li t0, 0x8000
    mtc0 t0, ulimit
    li t0, 0x474F4C59
    sw t0, LOG(zero)
    sw zero, LOG_LEN(zero)
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
    sw t0, -32(sp)
    mfc0 k0, cause
    addi k0, k0, -3
    teq k0, zero
    beq do_sys
    mfc0 k0, cause
    addi k0, k0, -2
    teq k0, zero
    beq do_kill
    mfc0 k0, cause
    addi k0, k0, -8
    teq k0, zero
    beq do_kill
    li k0, 0x4E41504B
    sw k0, LOG(zero)
    lw sp, -4(sp)
    halt
do_kill:
    lw sp, -4(sp)
    halt
do_sys:
    mfc0 k0, epc
    addi k0, k0, -4
    lw k0, 0(k0)
    andi k0, k0, 0xFFFF
    addi k0, k0, -1
    teq k0, zero
    beq do_exit
    addi k0, k0, -1
    teq k0, zero
    beq do_write
    lw a0, -8(sp)
    li a4, 1
    j restore_eret
do_exit:
    lw sp, -4(sp)
    halt
do_write:
    mfc0 k0, ubase
    cmp a0, k0
    blo write_bad
    add k0, a0, a1
    blo write_bad
    mfc0 t0, ulimit
    cmp t0, k0
    blo write_bad
    lw t0, LOG_LEN(zero)
    li k0, LOG_CAP
    cmp t0, k0
    bhs write_full
    sub k0, k0, t0
    cmp k0, a1
    blo write_ncopy_k0
    move k0, a1
write_ncopy_k0:
    move a2, k0
    teq k0, zero
    beq write_ok_zero
    addi t0, t0, 0x808
copy_loop:
    lbu a3, 0(a0)
    sb a3, 0(t0)
    addi a0, a0, 1
    addi t0, t0, 1
    addi k0, k0, -1
    teq k0, zero
    bne copy_loop
    addi t0, t0, -0x808
    sw t0, LOG_LEN(zero)
    move a0, a2
    li a4, 0
    j restore_eret
write_ok_zero:
    move a0, zero
    li a4, 0
    j restore_eret
write_full:
    teq a1, zero
    beq write_ok_zero
    move a0, zero
    li a4, 2
    j restore_eret
write_bad:
    lw a0, -8(sp)
    li a4, 1
    j restore_eret
restore_eret:
    lw a1, -12(sp)
    lw a2, -16(sp)
    lw a3, -20(sp)
    lw ra, -28(sp)
    lw t0, -32(sp)
    lw sp, -4(sp)
    eret

.org 0x1000
    la a0, msg
    li a1, 3
    sys 2
    sys 1
msg:
    .byte 0x79 0x61 0x70
