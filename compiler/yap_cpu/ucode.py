"""v1 microcode ROM: fetch, SPECIAL add/sub/halt, illegal → trap 7."""

from compiler.yap_cpu.control import (
    A_PC,
    A_RF,
    ALU_ADD,
    ALU_PASS_A,
    ALU_SUB,
    B_FOUR,
    B_RF,
    DST_MAR,
    FLAG_ADD,
    FLAG_SUB,
    IDX_RS,
    IDX_RT,
    MEM_WORD,
    SEQ_DISPATCH,
    SEQ_GOTO,
    SEQ_HALT,
    SEQ_NEXT,
    SEQ_TRAP,
    pack_cw,
)
from compiler.yap_isa.encode import FUNCT, OPCODE_SPECIAL, unpack_r
from compiler.yap_isa.csrs import CAUSE_PRIV

U_FETCH = 0x00
U_ADD = 0x10
U_SUB = 0x18
U_HALT = 0x20
U_ILLEGAL = 0x28
ROM_SIZE = 256


def dispatch(ir: int) -> int:
    fields = unpack_r(ir)
    if fields["opcode"] == OPCODE_SPECIAL:
        funct = fields["funct"]
        if funct == FUNCT["add"]:
            return U_ADD
        if funct == FUNCT["sub"]:
            return U_SUB
        if funct == FUNCT["halt"]:
            return U_HALT
    return U_ILLEGAL


def _alu_r(alu_op: int, flag_mode: int) -> list:
    return [
        pack_cw(seq=SEQ_NEXT, re_a=1, re_b=1, idx_a=IDX_RS, idx_b=IDX_RT),
        pack_cw(
            seq=SEQ_NEXT,
            alu_op=alu_op,
            a_sel=A_RF,
            b_sel=B_RF,
            we_rf=1,
            we_flags=1,
            flag_mode=flag_mode,
        ),
        pack_cw(seq=SEQ_GOTO, uimm=U_FETCH, alu_op=ALU_ADD, a_sel=A_PC, b_sel=B_FOUR, we_pc=1),
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
    for i, word in enumerate(_alu_r(ALU_ADD, FLAG_ADD)):
        rom[U_ADD + i] = word
    for i, word in enumerate(_alu_r(ALU_SUB, FLAG_SUB)):
        rom[U_SUB + i] = word
    rom[U_HALT] = pack_cw(seq=SEQ_HALT)
    rom[U_ILLEGAL] = pack_cw(seq=SEQ_TRAP, uimm=CAUSE_PRIV)
    return rom
