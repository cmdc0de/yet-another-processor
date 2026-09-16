"""m1 behavioral model: 32 GPRs, wired r0–r2, FLAGS, PC+4, SPECIAL ALU ops."""

from compiler.yap_isa.encode import FUNCT, OPCODE_SPECIAL, unpack_r

MASK = 0xFFFFFFFF
WORD_BYTES = 4


def _u32(x: int) -> int:
    return x & MASK


def _sign(x: int) -> int:
    return (x >> 31) & 1


class Flags:
    __slots__ = ("z", "n", "c", "v")

    def __init__(self):
        self.z = 0
        self.n = 0
        self.c = 0
        self.v = 0

    def set_zn(self, result: int) -> None:
        result = _u32(result)
        self.z = int(result == 0)
        self.n = _sign(result)

    def as_tuple(self):
        return (self.z, self.n, self.c, self.v)


class Cpu:
    def __init__(self):
        self._gprs = [0] * 32
        self.pc = 0
        self.flags = Flags()
        self._force_wired()

    def _force_wired(self) -> None:
        self._gprs[0] = 0
        self._gprs[1] = 1
        self._gprs[2] = MASK

    def read(self, idx: int) -> int:
        if not (0 <= idx < 32):
            raise ValueError(f"register index out of range: {idx}")
        if idx == 0:
            return 0
        if idx == 1:
            return 1
        if idx == 2:
            return MASK
        return _u32(self._gprs[idx])

    def write(self, idx: int, value: int) -> None:
        if not (0 <= idx < 32):
            raise ValueError(f"register index out of range: {idx}")
        if idx <= 2:
            return
        self._gprs[idx] = _u32(value)

    def gprs_snapshot(self) -> tuple:
        return tuple(self.read(i) for i in range(32))

    def _set_zncv_add(self, rs: int, rt: int, result: int, carry: int) -> None:
        self.flags.c = carry
        self.flags.v = int(_sign(rs) == _sign(rt) and _sign(result) != _sign(rs))
        self.flags.set_zn(result)

    def _set_zncv_sub(self, rs: int, rt: int, result: int) -> None:
        self.flags.c = int(rs < rt)
        self.flags.v = int(_sign(rs) != _sign(rt) and _sign(result) != _sign(rs))
        self.flags.set_zn(result)

    def _alu_add(self, rs: int, rt: int) -> int:
        raw = rs + rt
        result = _u32(raw)
        self._set_zncv_add(rs, rt, result, int(raw > MASK))
        return result

    def _alu_sub(self, rs: int, rt: int) -> int:
        result = _u32(rs - rt)
        self._set_zncv_sub(rs, rt, result)
        return result

    def _alu_logic(self, result: int) -> int:
        result = _u32(result)
        self.flags.c = 0
        self.flags.v = 0
        self.flags.set_zn(result)
        return result

    def _alu_sll(self, rs: int, shamt: int) -> int:
        rs = _u32(rs)
        if shamt == 0:
            c = 0
            result = rs
        else:
            c = (rs >> (32 - shamt)) & 1
            result = _u32(rs << shamt)
        self.flags.c = c
        self.flags.v = 0
        self.flags.set_zn(result)
        return result

    def step(self, word: int) -> None:
        fields = unpack_r(word)
        if fields["opcode"] != OPCODE_SPECIAL:
            raise ValueError(f"m1 only executes SPECIAL, opcode={fields['opcode']}")
        rd, rs_i, rt_i = fields["rd"], fields["rs"], fields["rt"]
        shamt, funct = fields["shamt"], fields["funct"]
        rs, rt = self.read(rs_i), self.read(rt_i)
        write = True
        if funct == FUNCT["add"]:
            result = self._alu_add(rs, rt)
        elif funct == FUNCT["sub"]:
            result = self._alu_sub(rs, rt)
        elif funct == FUNCT["and"]:
            result = self._alu_logic(rs & rt)
        elif funct == FUNCT["or"]:
            result = self._alu_logic(rs | rt)
        elif funct == FUNCT["xor"]:
            result = self._alu_logic(rs ^ rt)
        elif funct == FUNCT["not"]:
            result = self._alu_logic(~rs)
        elif funct == FUNCT["sll"]:
            result = self._alu_sll(rs, shamt)
        elif funct == FUNCT["cmp"]:
            self._alu_sub(rs, rt)
            write = False
            result = 0
        elif funct == FUNCT["test"]:
            self._alu_logic(rs & rt)
            write = False
            result = 0
        elif funct == FUNCT["teq"]:
            result = _u32(rs ^ rt)
            self.flags.z = int(result == 0)
            self.flags.n = 0
            self.flags.c = 0
            self.flags.v = 0
            write = False
        else:
            raise ValueError(f"funct not in m1: {funct:#08b}")
        if write:
            self.write(rd, result)
        self._force_wired()
        self.pc = _u32(self.pc + WORD_BYTES)
