"""R-type and I-type pack/unpack. Little-endian 32-bit words."""

from compiler.yap_isa.regs import parse_reg

OPCODE_SPECIAL = 0b000000
OPCODE = {
    "special": OPCODE_SPECIAL,
    "addi": 0b001000,
    "adr": 0b001001,
    "andi": 0b001100,
    "ori": 0b001101,
    "xori": 0b001110,
    "lui": 0b001111,
}

FUNCT = {
    "sll": 0b000000,
    "srl": 0b000010,
    "sra": 0b000011,
    "sllv": 0b000100,
    "srlv": 0b000110,
    "srav": 0b000111,
    "mul": 0b011000,
    "add": 0b100000,
    "sub": 0b100010,
    "and": 0b100100,
    "or": 0b100101,
    "xor": 0b100110,
    "not": 0b100111,
    "test": 0b101000,
    "teq": 0b101001,
    "cmp": 0b101010,
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


def parse_imm16(text: str) -> int:
    value = int(text, 0)
    if value < -0x8000 or value > 0xFFFF:
        raise ValueError(f"imm16 out of range: {text}")
    return value & 0xFFFF


def assemble(text: str) -> int:
    """Assemble one m1/m2 instruction."""
    parts = text.replace(",", " ").split()
    if not parts:
        raise ValueError("empty instruction")
    op = parts[0].lower()
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
    if op in ("sllv", "srlv", "srav", "add", "sub", "and", "or", "xor", "mul"):
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
