"""64-bit microcode control word (docs/cpu/design.md). Bit 0 is LSB."""

from collections import namedtuple

SEQ_NEXT = 0
SEQ_DISPATCH = 1
SEQ_GOTO = 2
SEQ_HALT = 3
SEQ_TRAP = 4
SEQ_ERET = 5
SEQ_SKIP_IF = 6
SEQ_SKIP_UNLESS = 7

ALU_ADD = 0
ALU_SUB = 1
ALU_AND = 2
ALU_OR = 3
ALU_XOR = 4
ALU_NOT = 5
ALU_SLL = 6
ALU_SRL = 7
ALU_SRA = 8
ALU_MUL = 9
ALU_DIV = 10
ALU_PASS_A = 11
ALU_PASS_B = 12
ALU_LUI = 13

A_RF = 0
A_PC = 1
A_EPC = 2
A_MDR = 3
A_CSR = 4
A_ZERO = 5
A_FOUR = 6
A_JTARGET = 7

B_RF = 0
B_IMM_SE = 1
B_IMM_ZE = 2
B_SHAMT = 3
B_RT5 = 4
B_FOUR = 5
B_ZERO = 6
B_BROFF = 7

DST_NONE = 0
DST_RF = 1
DST_PC = 2
DST_IR = 3
DST_MAR = 4
DST_MDR = 5
DST_CSR = 6
DST_FLAGS = 7

IDX_RS = 0
IDX_RT = 1
IDX_RD = 2
IDX_RA = 3

MEM_BYTE = 0
MEM_HALF = 1
MEM_WORD = 2

FLAG_ADD = 0
FLAG_SUB = 1
FLAG_LOGIC = 2
FLAG_SHIFT = 3
FLAG_TEQ = 4
FLAG_TEST = 5
FLAG_MULDIV = 6

Cw = namedtuple(
    "Cw",
    "seq uimm alu_op a_sel b_sel dst re_a re_b we_rf we_ir mem_re mem_we mem_sz "
    "we_flags re_csr we_csr we_pc idx_a idx_b load_sext irq_chk flag_mode csr_idx",
)


def pack_cw(
    seq=0,
    uimm=0,
    alu_op=0,
    a_sel=0,
    b_sel=0,
    dst=0,
    re_a=0,
    re_b=0,
    we_rf=0,
    we_ir=0,
    mem_re=0,
    mem_we=0,
    mem_sz=0,
    we_flags=0,
    re_csr=0,
    we_csr=0,
    we_pc=0,
    idx_a=0,
    idx_b=0,
    load_sext=0,
    irq_chk=0,
    flag_mode=0,
    csr_idx=0,
) -> int:
    w = 0
    w |= seq & 7
    w |= (uimm & 0xFF) << 3
    w |= (alu_op & 0xF) << 11
    w |= (a_sel & 7) << 15
    w |= (b_sel & 7) << 18
    w |= (dst & 7) << 21
    w |= (re_a & 1) << 24
    w |= (re_b & 1) << 25
    w |= (we_rf & 1) << 26
    w |= (we_ir & 1) << 27
    w |= (mem_re & 1) << 28
    w |= (mem_we & 1) << 29
    w |= (mem_sz & 3) << 30
    w |= (we_flags & 1) << 32
    w |= (re_csr & 1) << 33
    w |= (we_csr & 1) << 34
    w |= (we_pc & 1) << 35
    w |= (idx_a & 3) << 36
    w |= (idx_b & 3) << 38
    w |= (load_sext & 1) << 40
    w |= (irq_chk & 1) << 41
    w |= (flag_mode & 7) << 42
    w |= (csr_idx & 7) << 45
    return w


def unpack_cw(word: int) -> Cw:
    word = int(word) & ((1 << 64) - 1)
    return Cw(
        seq=word & 7,
        uimm=(word >> 3) & 0xFF,
        alu_op=(word >> 11) & 0xF,
        a_sel=(word >> 15) & 7,
        b_sel=(word >> 18) & 7,
        dst=(word >> 21) & 7,
        re_a=(word >> 24) & 1,
        re_b=(word >> 25) & 1,
        we_rf=(word >> 26) & 1,
        we_ir=(word >> 27) & 1,
        mem_re=(word >> 28) & 1,
        mem_we=(word >> 29) & 1,
        mem_sz=(word >> 30) & 3,
        we_flags=(word >> 32) & 1,
        re_csr=(word >> 33) & 1,
        we_csr=(word >> 34) & 1,
        we_pc=(word >> 35) & 1,
        idx_a=(word >> 36) & 3,
        idx_b=(word >> 38) & 3,
        load_sext=(word >> 40) & 1,
        irq_chk=(word >> 41) & 1,
        flag_mode=(word >> 42) & 7,
        csr_idx=(word >> 45) & 7,
    )
