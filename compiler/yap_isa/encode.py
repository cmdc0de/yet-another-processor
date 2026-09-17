"""R-type, I-type, and J-type pack/unpack. Little-endian 32-bit words."""

import re

from compiler.yap_isa.csrs import COP0_MFC0, COP0_MTC0, parse_csr
from compiler.yap_isa.regs import parse_reg

MASK_ADDR = 0xFFFFFFFF
_MEM_OP = re.compile(r"^(-?(?:0x[0-9a-fA-F]+|\d+))\((\w+)\)$")

OPCODE_SPECIAL = 0b000000
OPCODE = {
    "special": OPCODE_SPECIAL,
    "j": 0b000010,
    "jal": 0b000011,
    "bcc": 0b000100,
    "addi": 0b001000,
    "adr": 0b001001,
    "sys": 0b001010,
    "andi": 0b001100,
    "ori": 0b001101,
    "xori": 0b001110,
    "lui": 0b001111,
    "cop0": 0b010000,
    "lb": 0b100000,
    "lh": 0b100001,
    "lw": 0b100011,
    "lbu": 0b100100,
    "lhu": 0b100101,
    "sb": 0b101000,
    "sh": 0b101001,
    "sw": 0b101011,
}

FUNCT = {
    "sll": 0b000000,
    "srl": 0b000010,
    "sra": 0b000011,
    "sllv": 0b000100,
    "srlv": 0b000110,
    "srav": 0b000111,
    "jr": 0b001000,
    "jalr": 0b001001,
    "mul": 0b011000,
    "div": 0b011010,
    "add": 0b100000,
    "sub": 0b100010,
    "and": 0b100100,
    "or": 0b100101,
    "xor": 0b100110,
    "not": 0b100111,
    "test": 0b101000,
    "teq": 0b101001,
    "cmp": 0b101010,
    "halt": 0b101100,
    "eret": 0b101101,
}

COND = {
    "eq": 0b0000,
    "ne": 0b0001,
    "lt": 0b0010,
    "ge": 0b0011,
    "lo": 0b0100,
    "hs": 0b0101,
    "le": 0b0110,
    "gt": 0b0111,
    "mi": 0b1000,
    "pl": 0b1001,
}

BRANCH_MNEMONIC = {
    "beq": "eq",
    "bne": "ne",
    "blt": "lt",
    "bge": "ge",
    "blo": "lo",
    "bhs": "hs",
    "ble": "le",
    "bgt": "gt",
    "bmi": "mi",
    "bpl": "pl",
}


def pack_r(rd: int, rs: int, rt: int, shamt: int, funct: int, opcode: int = OPCODE_SPECIAL) -> int:
    if not (0 <= rd < 32 and 0 <= rs < 32 and 0 <= rt < 32):
        raise ValueError("register index out of range")
    if not (0 <= shamt < 32):
        raise ValueError("shamt out of range")
    if not (0 <= funct < 64) or not (0 <= opcode < 64):
        raise ValueError("opcode/funct out of range")
    word = (
        ((opcode & 0x3F) << 26)
        | ((rd & 0x1F) << 21)
        | ((rs & 0x1F) << 16)
        | ((rt & 0x1F) << 11)
        | ((shamt & 0x1F) << 6)
        | (funct & 0x3F)
    )
    return word & 0xFFFFFFFF


def unpack_r(word: int) -> dict:
    word &= 0xFFFFFFFF
    return {
        "opcode": (word >> 26) & 0x3F,
        "rd": (word >> 21) & 0x1F,
        "rs": (word >> 16) & 0x1F,
        "rt": (word >> 11) & 0x1F,
        "shamt": (word >> 6) & 0x1F,
        "funct": word & 0x3F,
        "imm16": word & 0xFFFF,
        "target26": word & 0x03FFFFFF,
        "cond": (word >> 22) & 0xF,
        "imm22": word & 0x3FFFFF,
        "bytes": (word).to_bytes(4, "little"),
    }


def pack_i(opcode: int, rd: int, rs: int, imm16: int) -> int:
    if not (0 <= rd < 32 and 0 <= rs < 32):
        raise ValueError("register index out of range")
    if not (0 <= opcode < 64):
        raise ValueError("opcode out of range")
    imm16 &= 0xFFFF
    word = ((opcode & 0x3F) << 26) | ((rd & 0x1F) << 21) | ((rs & 0x1F) << 16) | imm16
    return word & 0xFFFFFFFF


def sext16(imm16: int) -> int:
    imm16 &= 0xFFFF
    if imm16 & 0x8000:
        return imm16 - 0x10000
    return imm16


def pack_j(opcode: int, target26: int) -> int:
    if not (0 <= opcode < 64):
        raise ValueError("opcode out of range")
    return (((opcode & 0x3F) << 26) | (target26 & 0x03FFFFFF)) & 0xFFFFFFFF


def pack_b(cond: int, imm22: int, opcode: int = OPCODE["bcc"]) -> int:
    if not (0 <= cond < 16):
        raise ValueError("cond out of range")
    return (((opcode & 0x3F) << 26) | ((cond & 0xF) << 22) | (imm22 & 0x3FFFFF)) & 0xFFFFFFFF


def sext22(imm22: int) -> int:
    imm22 &= 0x3FFFFF
    if imm22 & 0x200000:
        return imm22 - 0x400000
    return imm22


def parse_imm16(text: str) -> int:
    value = int(text, 0)
    if value < -0x8000 or value > 0xFFFF:
        raise ValueError(f"imm16 out of range: {text}")
    return value & 0xFFFF


def parse_mem_operand(text: str) -> tuple:
    match = _MEM_OP.match(text.strip())
    if not match:
        raise ValueError(f"expected off(rs), got {text!r}")
    return parse_imm16(match.group(1)), parse_reg(match.group(2))


def assemble(text: str, pc: int = 0) -> int:
    """Assemble one instruction. Branches encode a PC-absolute target using `pc`."""
    parts = text.replace(",", " ").split()
    if not parts:
        raise ValueError("empty instruction")
    op = parts[0].lower()
    if op == "sys":
        if len(parts) != 2:
            raise ValueError("sys imm")
        return pack_i(OPCODE["sys"], 0, 0, parse_imm16(parts[1]))
    if op == "eret":
        if len(parts) != 1:
            raise ValueError("eret takes no operands")
        return pack_r(0, 0, 0, 0, FUNCT["eret"])
    if op == "mfc0":
        if len(parts) != 3:
            raise ValueError("mfc0 rd, csr")
        rd, csr = parse_reg(parts[1]), parse_csr(parts[2])
        return pack_r(rd, COP0_MFC0, csr, 0, 0, opcode=OPCODE["cop0"])
    if op == "mtc0":
        if len(parts) != 3:
            raise ValueError("mtc0 rd, csr")
        rd, csr = parse_reg(parts[1]), parse_csr(parts[2])
        return pack_r(rd, COP0_MTC0, csr, 0, 0, opcode=OPCODE["cop0"])
    if op == "halt":
        if len(parts) != 1:
            raise ValueError("halt takes no operands")
        return pack_r(0, 0, 0, 0, FUNCT["halt"])
    if op in BRANCH_MNEMONIC:
        if len(parts) != 2:
            raise ValueError(f"{op} target")
        addr = int(parts[1], 0) & MASK_ADDR
        if addr & 3:
            raise ValueError(f"{op} target must be word-aligned")
        next_pc = (pc + 4) & MASK_ADDR
        delta = (addr - next_pc) & MASK_ADDR
        if delta >= 0x80000000:
            delta -= 0x100000000
        if delta % 4:
            raise ValueError(f"{op} offset not word-aligned")
        imm22 = delta >> 2
        if imm22 < -0x200000 or imm22 > 0x1FFFFF:
            raise ValueError(f"{op} offset out of range")
        return pack_b(COND[BRANCH_MNEMONIC[op]], imm22 & 0x3FFFFF)
    if op == "nop":
        if len(parts) != 1:
            raise ValueError("nop takes no operands")
        return pack_r(0, 0, 0, 0, FUNCT["sll"])
    if op == "not":
        if len(parts) != 3:
            raise ValueError("not rd, rs")
        rd, rs = parse_reg(parts[1]), parse_reg(parts[2])
        return pack_r(rd, rs, 0, 0, FUNCT["not"])
    if op in ("cmp", "test", "teq"):
        if len(parts) != 3:
            raise ValueError(f"{op} rs, rt")
        rs, rt = parse_reg(parts[1]), parse_reg(parts[2])
        return pack_r(0, rs, rt, 0, FUNCT[op])
    if op in ("sll", "srl", "sra"):
        if len(parts) != 4:
            raise ValueError(f"{op} rd, rs, shamt")
        rd, rs, shamt = parse_reg(parts[1]), parse_reg(parts[2]), int(parts[3], 0)
        return pack_r(rd, rs, 0, shamt, FUNCT[op])
    if op == "jr":
        if len(parts) != 2:
            raise ValueError("jr rs")
        rs = parse_reg(parts[1])
        return pack_r(0, rs, 0, 0, FUNCT["jr"])
    if op == "jalr":
        if len(parts) == 2:
            rd, rs = parse_reg("ra"), parse_reg(parts[1])
        elif len(parts) == 3:
            rd, rs = parse_reg(parts[1]), parse_reg(parts[2])
        else:
            raise ValueError("jalr rd, rs")
        return pack_r(rd, rs, 0, 0, FUNCT["jalr"])
    if op in ("j", "jal"):
        if len(parts) != 2:
            raise ValueError(f"{op} target")
        addr = int(parts[1], 0) & MASK_ADDR
        if addr & 3:
            raise ValueError(f"{op} target must be word-aligned")
        return pack_j(OPCODE[op], (addr >> 2) & 0x03FFFFFF)
    if op in ("lw", "lh", "lb", "lbu", "lhu", "sw", "sh", "sb"):
        if len(parts) != 3:
            raise ValueError(f"{op} rd, off(rs)")
        rd = parse_reg(parts[1])
        off, rs = parse_mem_operand(parts[2])
        return pack_i(OPCODE[op], rd, rs, off)
    if op in ("sllv", "srlv", "srav", "add", "sub", "and", "or", "xor", "mul", "div"):
        if len(parts) != 4:
            raise ValueError(f"{op} rd, rs, rt")
        rd, rs, rt = parse_reg(parts[1]), parse_reg(parts[2]), parse_reg(parts[3])
        return pack_r(rd, rs, rt, 0, FUNCT[op])
    if op in ("addi", "andi", "ori", "xori"):
        if len(parts) != 4:
            raise ValueError(f"{op} rd, rs, imm")
        rd, rs, imm = parse_reg(parts[1]), parse_reg(parts[2]), parse_imm16(parts[3])
        return pack_i(OPCODE[op], rd, rs, imm)
    if op == "lui":
        if len(parts) != 3:
            raise ValueError("lui rd, imm")
        rd, imm = parse_reg(parts[1]), parse_imm16(parts[2])
        return pack_i(OPCODE["lui"], rd, 0, imm)
    if op == "adr":
        if len(parts) != 3:
            raise ValueError("adr rd, imm")
        rd, imm = parse_reg(parts[1]), parse_imm16(parts[2])
        return pack_i(OPCODE["adr"], rd, 0, imm)
    raise ValueError(f"unsupported mnemonic: {op}")


def nop_word() -> int:
    return assemble("nop")
