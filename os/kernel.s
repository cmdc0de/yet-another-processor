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
    mfc1 t0, f0
    sw t0, -160(sp)
    mfc1 t0, f1
    sw t0, -156(sp)
    mfc1 t0, f2
    sw t0, -152(sp)
    mfc1 t0, f3
    sw t0, -148(sp)
    mfc1 t0, f4
    sw t0, -144(sp)
    mfc1 t0, f5
    sw t0, -140(sp)
    mfc1 t0, f6
    sw t0, -136(sp)
    mfc1 t0, f7
    sw t0, -132(sp)
    mfc1 t0, f8
    sw t0, -128(sp)
    mfc1 t0, f9
    sw t0, -124(sp)
    mfc1 t0, f10
    sw t0, -120(sp)
    mfc1 t0, f11
    sw t0, -116(sp)
    mfc1 t0, f12
    sw t0, -112(sp)
    mfc1 t0, f13
    sw t0, -108(sp)
    mfc1 t0, f14
    sw t0, -104(sp)
    mfc1 t0, f15
    sw t0, -100(sp)
    mfc1 t0, f16
    sw t0, -96(sp)
    mfc1 t0, f17
    sw t0, -92(sp)
    mfc1 t0, f18
    sw t0, -88(sp)
    mfc1 t0, f19
    sw t0, -84(sp)
    mfc1 t0, f20
    sw t0, -80(sp)
    mfc1 t0, f21
    sw t0, -76(sp)
    mfc1 t0, f22
    sw t0, -72(sp)
    mfc1 t0, f23
    sw t0, -68(sp)
    mfc1 t0, f24
    sw t0, -64(sp)
    mfc1 t0, f25
    sw t0, -60(sp)
    mfc1 t0, f26
    sw t0, -56(sp)
    mfc1 t0, f27
    sw t0, -52(sp)
    mfc1 t0, f28
    sw t0, -48(sp)
    mfc1 t0, f29
    sw t0, -44(sp)
    mfc1 t0, f30
    sw t0, -40(sp)
    mfc1 t0, f31
    sw t0, -36(sp)
    mtc1 zero, f0
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
    lw t0, -160(sp)
    mtc1 t0, f0
    lw t0, -156(sp)
    mtc1 t0, f1
    lw t0, -152(sp)
    mtc1 t0, f2
    lw t0, -148(sp)
    mtc1 t0, f3
    lw t0, -144(sp)
    mtc1 t0, f4
    lw t0, -140(sp)
    mtc1 t0, f5
    lw t0, -136(sp)
    mtc1 t0, f6
    lw t0, -132(sp)
    mtc1 t0, f7
    lw t0, -128(sp)
    mtc1 t0, f8
    lw t0, -124(sp)
    mtc1 t0, f9
    lw t0, -120(sp)
    mtc1 t0, f10
    lw t0, -116(sp)
    mtc1 t0, f11
    lw t0, -112(sp)
    mtc1 t0, f12
    lw t0, -108(sp)
    mtc1 t0, f13
    lw t0, -104(sp)
    mtc1 t0, f14
    lw t0, -100(sp)
    mtc1 t0, f15
    lw t0, -96(sp)
    mtc1 t0, f16
    lw t0, -92(sp)
    mtc1 t0, f17
    lw t0, -88(sp)
    mtc1 t0, f18
    lw t0, -84(sp)
    mtc1 t0, f19
    lw t0, -80(sp)
    mtc1 t0, f20
    lw t0, -76(sp)
    mtc1 t0, f21
    lw t0, -72(sp)
    mtc1 t0, f22
    lw t0, -68(sp)
    mtc1 t0, f23
    lw t0, -64(sp)
    mtc1 t0, f24
    lw t0, -60(sp)
    mtc1 t0, f25
    lw t0, -56(sp)
    mtc1 t0, f26
    lw t0, -52(sp)
    mtc1 t0, f27
    lw t0, -48(sp)
    mtc1 t0, f28
    lw t0, -44(sp)
    mtc1 t0, f29
    lw t0, -40(sp)
    mtc1 t0, f30
    lw t0, -36(sp)
    mtc1 t0, f31
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
