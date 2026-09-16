"""R-type pack/unpack for m1 SPECIAL ops. Little-endian 32-bit words."""

from compiler.yap_isa.regs import parse_reg

OPCODE_SPECIAL = 0b000000

FUNCT = {
    "sll": 0b000000,
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
        "bytes": (word).to_bytes(4, "little"),
    }


def assemble(text: str) -> int:
    """Assemble one m1 instruction. Mnemonics: add/sub/and/or/xor/not/sll/nop/cmp/test/teq."""
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
    if op == "sll":
        if len(parts) != 4:
            raise ValueError("sll rd, rs, shamt")
        rd, rs, shamt = parse_reg(parts[1]), parse_reg(parts[2]), int(parts[3], 0)
        return pack_r(rd, rs, 0, shamt, FUNCT["sll"])
    if op in ("add", "sub", "and", "or", "xor"):
        if len(parts) != 4:
            raise ValueError(f"{op} rd, rs, rt")
        rd, rs, rt = parse_reg(parts[1]), parse_reg(parts[2]), parse_reg(parts[3])
        return pack_r(rd, rs, rt, 0, FUNCT[op])
    raise ValueError(f"unsupported m1 mnemonic: {op}")


def nop_word() -> int:
    return assemble("nop")
