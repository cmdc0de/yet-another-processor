"""v1 microcode ROM: fetch, integer ALU/shifts/immediates, halt, illegal → trap 7."""

from compiler.yap_cpu.control import (
    A_CSR,
    A_JTARGET,
    A_MDR,
    A_PC,
    A_RF,
    ALU_ADD,
    ALU_AND,
    ALU_DIV,
    ALU_LUI,
    ALU_MUL,
    ALU_NOT,
    ALU_OR,
    ALU_PASS_A,
    ALU_PASS_B,
    ALU_SLL,
    ALU_SRA,
    ALU_SRL,
    ALU_SUB,
    ALU_XOR,
    B_BROFF,
    B_FOUR,
    B_IMM_SE,
    B_IMM_ZE,
    B_RF,
    B_SHAMT,
    DST_MAR,
    DST_MDR,
    FLAG_ADD,
    FLAG_LOGIC,
    FLAG_MULDIV,
    FLAG_SHIFT,
    FLAG_SUB,
    FLAG_TEQ,
    FLAG_TEST,
    IDX_RD,
    IDX_RS,
    IDX_RT,
    MEM_BYTE,
    MEM_HALF,
    MEM_WORD,
    SEQ_DISPATCH,
    SEQ_ERET,
    SEQ_GOTO,
    SEQ_HALT,
    SEQ_NEXT,
    SEQ_SKIP_IF,
    SEQ_TRAP,
    pack_cw,
)
from compiler.yap_isa.encode import FUNCT, OPCODE, OPCODE_SPECIAL, unpack_r
from compiler.yap_isa.csrs import (
    CAUSE_COP,
    CAUSE_PRIV,
    CAUSE_SYS,
    COP0_MFC0,
    COP0_MTC0,
    COP1_MFC1,
    COP1_MTC1,
)

U_FETCH = 0x00
U_ADD = 0x08
U_SUB = 0x0C
U_AND = 0x10
U_OR = 0x14
U_XOR = 0x18
U_NOT = 0x1C
U_SLL = 0x20
U_SRL = 0x24
U_SRA = 0x28
U_SLLV = 0x2C
U_SRLV = 0x30
U_SRAV = 0x34
U_MUL = 0x38
U_DIV = 0x3C
U_CMP = 0x40
U_TEST = 0x44
U_TEQ = 0x48
U_ADDI = 0x4C
U_ANDI = 0x50
U_ORI = 0x54
U_XORI = 0x58
U_LUI = 0x5C
U_ADR = 0x60
U_HALT = 0x64
U_ILLEGAL = 0x68
U_LW = 0x6C
U_LH = 0x70
U_LB = 0x74
U_LBU = 0x78
U_LHU = 0x7C
U_SW = 0x80
U_SH = 0x84
U_SB = 0x88
U_MFC0 = 0x8C
U_MTC0 = 0x90
U_MFC1 = 0x94
U_MTC1 = 0x98
U_SYS = 0x9C
U_ERET = 0xA0
U_COP_UNIMP = 0xA4
U_J = 0xA8
U_JAL = 0xAC
U_JR = 0xB0
U_JALR = 0xB4
U_BCC = 0xB8
ROM_SIZE = 256

_SPECIAL = {
    FUNCT["add"]: U_ADD,
    FUNCT["sub"]: U_SUB,
    FUNCT["and"]: U_AND,
    FUNCT["or"]: U_OR,
    FUNCT["xor"]: U_XOR,
    FUNCT["not"]: U_NOT,
    FUNCT["sll"]: U_SLL,
    FUNCT["srl"]: U_SRL,
    FUNCT["sra"]: U_SRA,
    FUNCT["sllv"]: U_SLLV,
    FUNCT["srlv"]: U_SRLV,
    FUNCT["srav"]: U_SRAV,
    FUNCT["mul"]: U_MUL,
    FUNCT["div"]: U_DIV,
    FUNCT["cmp"]: U_CMP,
    FUNCT["test"]: U_TEST,
    FUNCT["teq"]: U_TEQ,
    FUNCT["halt"]: U_HALT,
    FUNCT["eret"]: U_ERET,
    FUNCT["jr"]: U_JR,
    FUNCT["jalr"]: U_JALR,
}

_OPCODE = {
    OPCODE["addi"]: U_ADDI,
    OPCODE["andi"]: U_ANDI,
    OPCODE["ori"]: U_ORI,
    OPCODE["xori"]: U_XORI,
    OPCODE["lui"]: U_LUI,
    OPCODE["adr"]: U_ADR,
    OPCODE["lw"]: U_LW,
    OPCODE["lh"]: U_LH,
    OPCODE["lb"]: U_LB,
    OPCODE["lbu"]: U_LBU,
    OPCODE["lhu"]: U_LHU,
    OPCODE["sw"]: U_SW,
    OPCODE["sh"]: U_SH,
    OPCODE["sb"]: U_SB,
    OPCODE["j"]: U_J,
    OPCODE["jal"]: U_JAL,
    OPCODE["bcc"]: U_BCC,
}


def dispatch(ir: int) -> int:
    fields = unpack_r(ir)
    op = fields["opcode"]
    if op == OPCODE_SPECIAL:
        return _SPECIAL.get(fields["funct"], U_ILLEGAL)
    if op == OPCODE["sys"]:
        return U_SYS
    if op == OPCODE["cop0"]:
        rs = fields["rs"]
        if rs == COP0_MFC0:
            return U_MFC0
        if rs == COP0_MTC0:
            return U_MTC0
        return U_ILLEGAL
    if op == OPCODE["cop1"]:
        rs = fields["rs"]
        if rs == COP1_MFC1:
            return U_MFC1
        if rs == COP1_MTC1:
            return U_MTC1
        return U_COP_UNIMP
    return _OPCODE.get(op, U_ILLEGAL)


def _pc4():
    return pack_cw(seq=SEQ_GOTO, uimm=U_FETCH, alu_op=ALU_ADD, a_sel=A_PC, b_sel=B_FOUR, we_pc=1)


def _r_rr(alu_op: int, flag_mode: int, we_rf: int = 1) -> list:
    return [
        pack_cw(seq=SEQ_NEXT, re_a=1, re_b=1, idx_a=IDX_RS, idx_b=IDX_RT),
        pack_cw(
            seq=SEQ_NEXT,
            alu_op=alu_op,
            a_sel=A_RF,
            b_sel=B_RF,
            we_rf=we_rf,
            we_flags=1,
            flag_mode=flag_mode,
        ),
        _pc4(),
    ]


def _r_rs(alu_op: int, flag_mode: int) -> list:
    return [
        pack_cw(seq=SEQ_NEXT, re_a=1, idx_a=IDX_RS),
        pack_cw(
            seq=SEQ_NEXT,
            alu_op=alu_op,
            a_sel=A_RF,
            we_rf=1,
            we_flags=1,
            flag_mode=flag_mode,
        ),
        _pc4(),
    ]


def _shift_imm(alu_op: int) -> list:
    return [
        pack_cw(seq=SEQ_NEXT, re_a=1, idx_a=IDX_RS),
        pack_cw(
            seq=SEQ_NEXT,
            alu_op=alu_op,
            a_sel=A_RF,
            b_sel=B_SHAMT,
            we_rf=1,
            we_flags=1,
            flag_mode=FLAG_SHIFT,
        ),
        _pc4(),
    ]


def _load(mem_sz: int, load_sext: int) -> list:
    return [
        pack_cw(seq=SEQ_NEXT, re_a=1, idx_a=IDX_RS),
        pack_cw(
            seq=SEQ_NEXT,
            alu_op=ALU_ADD,
            a_sel=A_RF,
            b_sel=B_IMM_SE,
            dst=DST_MAR,
            mem_re=1,
            mem_sz=mem_sz,
            load_sext=load_sext,
        ),
        pack_cw(seq=SEQ_NEXT, alu_op=ALU_PASS_A, a_sel=A_MDR, we_rf=1),
        _pc4(),
    ]


def _store(mem_sz: int) -> list:
    return [
        pack_cw(seq=SEQ_NEXT, re_a=1, re_b=1, idx_a=IDX_RS, idx_b=IDX_RD),
        pack_cw(seq=SEQ_NEXT, alu_op=ALU_ADD, a_sel=A_RF, b_sel=B_IMM_SE, dst=DST_MAR),
        pack_cw(
            seq=SEQ_NEXT,
            alu_op=ALU_PASS_B,
            b_sel=B_RF,
            dst=DST_MDR,
            mem_we=1,
            mem_sz=mem_sz,
        ),
        _pc4(),
    ]


def _i_alu(alu_op: int, b_sel: int, flag_mode: int) -> list:
    return [
        pack_cw(seq=SEQ_NEXT, re_a=1, idx_a=IDX_RS),
        pack_cw(
            seq=SEQ_NEXT,
            alu_op=alu_op,
            a_sel=A_RF,
            b_sel=b_sel,
            we_rf=1,
            we_flags=1,
            flag_mode=flag_mode,
        ),
        _pc4(),
    ]


def build_rom() -> list:
    rom = [pack_cw(seq=SEQ_TRAP, uimm=CAUSE_PRIV)] * ROM_SIZE
    rom[U_FETCH] = pack_cw(
        seq=SEQ_NEXT,
        alu_op=ALU_PASS_A,
        a_sel=A_PC,
        dst=DST_MAR,
        mem_re=1,
        mem_sz=MEM_WORD,
        irq_chk=1,
    )
    rom[U_FETCH + 1] = pack_cw(seq=SEQ_DISPATCH, we_ir=1)
    slots = {
        U_ADD: _r_rr(ALU_ADD, FLAG_ADD),
        U_SUB: _r_rr(ALU_SUB, FLAG_SUB),
        U_AND: _r_rr(ALU_AND, FLAG_LOGIC),
        U_OR: _r_rr(ALU_OR, FLAG_LOGIC),
        U_XOR: _r_rr(ALU_XOR, FLAG_LOGIC),
        U_NOT: _r_rs(ALU_NOT, FLAG_LOGIC),
        U_SLL: _shift_imm(ALU_SLL),
        U_SRL: _shift_imm(ALU_SRL),
        U_SRA: _shift_imm(ALU_SRA),
        U_SLLV: _r_rr(ALU_SLL, FLAG_SHIFT),
        U_SRLV: _r_rr(ALU_SRL, FLAG_SHIFT),
        U_SRAV: _r_rr(ALU_SRA, FLAG_SHIFT),
        U_MUL: _r_rr(ALU_MUL, FLAG_MULDIV),
        U_DIV: _r_rr(ALU_DIV, FLAG_MULDIV),
        U_CMP: _r_rr(ALU_SUB, FLAG_SUB, we_rf=0),
        U_TEST: _r_rr(ALU_AND, FLAG_TEST, we_rf=0),
        U_TEQ: _r_rr(ALU_XOR, FLAG_TEQ, we_rf=0),
        U_ADDI: _i_alu(ALU_ADD, B_IMM_SE, FLAG_ADD),
        U_ANDI: _i_alu(ALU_AND, B_IMM_ZE, FLAG_LOGIC),
        U_ORI: _i_alu(ALU_OR, B_IMM_ZE, FLAG_LOGIC),
        U_XORI: _i_alu(ALU_XOR, B_IMM_ZE, FLAG_LOGIC),
        U_LUI: [
            pack_cw(seq=SEQ_NEXT, alu_op=ALU_LUI, we_rf=1),
            _pc4(),
        ],
        U_ADR: [
            pack_cw(seq=SEQ_NEXT, alu_op=ALU_ADD, a_sel=A_PC, b_sel=B_FOUR, dst=DST_MDR),
            pack_cw(seq=SEQ_NEXT, alu_op=ALU_ADD, a_sel=A_MDR, b_sel=B_IMM_SE, we_rf=1),
            _pc4(),
        ],
        U_LW: _load(MEM_WORD, 0),
        U_LH: _load(MEM_HALF, 1),
        U_LB: _load(MEM_BYTE, 1),
        U_LBU: _load(MEM_BYTE, 0),
        U_LHU: _load(MEM_HALF, 0),
        U_SW: _store(MEM_WORD),
        U_SH: _store(MEM_HALF),
        U_SB: _store(MEM_BYTE),
        U_MFC0: [
            pack_cw(seq=SEQ_NEXT, re_csr=1, csr_idx=0, alu_op=ALU_PASS_A, a_sel=A_CSR, we_rf=1),
            _pc4(),
        ],
        U_MTC0: [
            pack_cw(seq=SEQ_NEXT, re_a=1, idx_a=IDX_RD),
            pack_cw(seq=SEQ_NEXT, alu_op=ALU_PASS_A, a_sel=A_RF, we_csr=1, csr_idx=0),
            _pc4(),
        ],
        U_MFC1: [
            pack_cw(seq=SEQ_NEXT, we_rf=1),
            _pc4(),
        ],
        U_MTC1: [
            pack_cw(seq=SEQ_NEXT, re_a=1, idx_a=IDX_RD),
            pack_cw(seq=SEQ_NEXT, we_csr=1),
            _pc4(),
        ],
        U_SYS: [pack_cw(seq=SEQ_TRAP, uimm=CAUSE_SYS)],
        U_ERET: [pack_cw(seq=SEQ_ERET)],
        U_COP_UNIMP: [pack_cw(seq=SEQ_TRAP, uimm=CAUSE_COP)],
        U_J: [
            pack_cw(seq=SEQ_GOTO, uimm=U_FETCH, alu_op=ALU_PASS_A, a_sel=A_JTARGET, we_pc=1),
        ],
        U_JAL: [
            pack_cw(seq=SEQ_NEXT, alu_op=ALU_ADD, a_sel=A_PC, b_sel=B_FOUR, we_rf=1),
            pack_cw(seq=SEQ_GOTO, uimm=U_FETCH, alu_op=ALU_PASS_A, a_sel=A_JTARGET, we_pc=1),
        ],
        U_JR: [
            pack_cw(seq=SEQ_NEXT, re_a=1, idx_a=IDX_RS),
            pack_cw(seq=SEQ_GOTO, uimm=U_FETCH, alu_op=ALU_PASS_A, a_sel=A_RF, we_pc=1),
        ],
        U_JALR: [
            pack_cw(seq=SEQ_NEXT, re_a=1, idx_a=IDX_RS),
            pack_cw(seq=SEQ_NEXT, alu_op=ALU_ADD, a_sel=A_PC, b_sel=B_FOUR, we_rf=1),
            pack_cw(seq=SEQ_GOTO, uimm=U_FETCH, alu_op=ALU_PASS_A, a_sel=A_RF, we_pc=1),
        ],
        U_BCC: [
            pack_cw(seq=SEQ_SKIP_IF),
            pack_cw(seq=SEQ_GOTO, uimm=U_FETCH, alu_op=ALU_ADD, a_sel=A_PC, b_sel=B_FOUR, we_pc=1),
            pack_cw(seq=SEQ_NEXT, alu_op=ALU_ADD, a_sel=A_PC, b_sel=B_FOUR, dst=DST_MDR),
            pack_cw(
                seq=SEQ_GOTO,
                uimm=U_FETCH,
                alu_op=ALU_ADD,
                a_sel=A_MDR,
                b_sel=B_BROFF,
                we_pc=1,
            ),
        ],
    }
    for addr, words in slots.items():
        for i, word in enumerate(words):
            rom[addr + i] = word
    rom[U_HALT] = pack_cw(seq=SEQ_HALT)
    rom[U_ILLEGAL] = pack_cw(seq=SEQ_TRAP, uimm=CAUSE_PRIV)
    return rom
