"""User C ABI helpers: stack grows down, 8-byte aligned at calls."""

from compiler.yap_isa.cpu import MASK, Cpu
from compiler.yap_isa.regs import NAME_TO_NUM

SP = NAME_TO_NUM["sp"]
STACK_ALIGN = 8
WORD = 4

# User C ABI set: not k0, not wired r0–r2.
USER_C_REGS = {
    "ra": 3,
    "sp": 4,
    "a0": 5,
    "a1": 6,
    "a2": 7,
    "a3": 8,
    "a4": 9,
    "t0": 10,
    "t1": 11,
    "t2": 12,
    "t3": 13,
    "t4": 14,
    "t5": 15,
    "s0": 16,
    "s1": 17,
    "s2": 18,
    "s3": 19,
    "s4": 20,
    "s5": 21,
    "s6": 22,
    "s7": 23,
    "s8": 24,
    "s9": 25,
    "s10": 26,
    "s11": 27,
    "t6": 28,
    "t7": 29,
    "fp": 30,
}

ABI_MAP = {
    "ra": 3,
    "sp": 4,
    "a0": 5,
    "a3": 8,
    "s0": 16,
    "s11": 27,
    "fp": 30,
    "k0": 31,
}


def push_word(cpu: Cpu, value: int) -> int:
    """Push a 32-bit word; stack grows down. Returns the new sp."""
    sp = (cpu.read(SP) - WORD) & MASK
    cpu.write(SP, sp)
    cpu.mem_store(sp, (value & MASK).to_bytes(WORD, "little"))
    return sp


def pop_word(cpu: Cpu) -> int:
    sp = cpu.read(SP)
    raw = int.from_bytes(cpu.mem_load(sp, WORD), "little")
    cpu.write(SP, (sp + WORD) & MASK)
    return raw
