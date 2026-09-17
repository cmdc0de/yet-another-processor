"""Behavioral model: GPRs, FLAGS, memory, DIV, load/store, jumps."""

from compiler.yap_isa.encode import COND, FUNCT, OPCODE, OPCODE_SPECIAL, sext16, sext22, unpack_r

MASK = 0xFFFFFFFF
WORD_BYTES = 4
CAUSE_ALIGN = 8


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
    def __init__(self, mem_size: int = 65536):
        self._gprs = [0] * 32
        self.pc = 0
        self.flags = Flags()
        self.cause = 0
        self.mem = bytearray(mem_size)
        self.halted = False
        self._pc_next = None
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
        shamt &= 31
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

    def _alu_srl(self, rs: int, shamt: int) -> int:
        rs = _u32(rs)
        shamt &= 31
        if shamt == 0:
            c = 0
            result = rs
        else:
            c = (rs >> (shamt - 1)) & 1
            result = rs >> shamt
        self.flags.c = c
        self.flags.v = 0
        self.flags.set_zn(result)
        return result

    def _alu_sra(self, rs: int, shamt: int) -> int:
        rs = _u32(rs)
        shamt &= 31
        signed = rs - 0x100000000 if _sign(rs) else rs
        if shamt == 0:
            c = 0
        else:
            c = (rs >> (shamt - 1)) & 1
        result = _u32(signed >> shamt)
        self.flags.c = c
        self.flags.v = 0
        self.flags.set_zn(result)
        return result

    def _alu_mul(self, rs: int, rt: int) -> int:
        result = _u32(rs * rt)
        self.flags.c = 0
        self.flags.v = 0
        self.flags.set_zn(result)
        return result

    def _alu_div(self, rs: int, rt: int) -> int:
        if rt == 0:
            result = 0
        else:
            result = _u32(rs // rt)
        self.flags.c = 0
        self.flags.v = 0
        self.flags.set_zn(result)
        return result

    def _addr(self, rs_i: int, imm16: int) -> int:
        return _u32(self.read(rs_i) + sext16(imm16))

    def _check_align(self, addr: int, size: int) -> bool:
        if addr % size != 0:
            self.cause = CAUSE_ALIGN
            return False
        return True

    def mem_store(self, addr: int, data: bytes) -> None:
        end = addr + len(data)
        if addr < 0 or end > len(self.mem):
            raise ValueError(f"memory store out of range: {addr}")
        self.mem[addr:end] = data

    def mem_load(self, addr: int, size: int) -> bytes:
        end = addr + size
        if addr < 0 or end > len(self.mem):
            raise ValueError(f"memory load out of range: {addr}")
        return bytes(self.mem[addr:end])

    def _load(self, rd: int, rs_i: int, imm16: int, size: int, signed: bool) -> None:
        addr = self._addr(rs_i, imm16)
        if not self._check_align(addr, size):
            return
        raw = int.from_bytes(self.mem_load(addr, size), "little")
        if signed:
            sign_bit = 1 << (size * 8 - 1)
            if raw & sign_bit:
                raw -= 1 << (size * 8)
            raw = _u32(raw)
        self.write(rd, raw)

    def _store(self, rd: int, rs_i: int, imm16: int, size: int) -> None:
        addr = self._addr(rs_i, imm16)
        if not self._check_align(addr, size):
            return
        value = self.read(rd) & ((1 << (size * 8)) - 1)
        self.mem_store(addr, value.to_bytes(size, "little"))

    def _jump_abs(self, target26: int) -> None:
        next_pc = _u32(self.pc + WORD_BYTES)
        self._pc_next = (next_pc & 0xF0000000) | ((target26 & 0x03FFFFFF) << 2)

    def _branch_taken(self, cond: int) -> bool:
        z, n, c, v = self.flags.z, self.flags.n, self.flags.c, self.flags.v
        nv = n ^ v
        if cond == COND["eq"]:
            return bool(z)
        if cond == COND["ne"]:
            return not z
        if cond == COND["lt"]:
            return bool(nv)
        if cond == COND["ge"]:
            return not nv
        if cond == COND["lo"]:
            return bool(c)
        if cond == COND["hs"]:
            return not c
        if cond == COND["le"]:
            return bool(z or nv)
        if cond == COND["gt"]:
            return not (z or nv)
        if cond == COND["mi"]:
            return bool(n)
        if cond == COND["pl"]:
            return not n
        raise ValueError(f"unknown branch cond: {cond}")

    def _step_special(self, fields: dict) -> None:
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
        elif funct == FUNCT["srl"]:
            result = self._alu_srl(rs, shamt)
        elif funct == FUNCT["sra"]:
            result = self._alu_sra(rs, shamt)
        elif funct == FUNCT["sllv"]:
            result = self._alu_sll(rs, rt & 31)
        elif funct == FUNCT["srlv"]:
            result = self._alu_srl(rs, rt & 31)
        elif funct == FUNCT["srav"]:
            result = self._alu_sra(rs, rt & 31)
        elif funct == FUNCT["mul"]:
            result = self._alu_mul(rs, rt)
        elif funct == FUNCT["div"]:
            result = self._alu_div(rs, rt)
        elif funct == FUNCT["jr"]:
            self._pc_next = rs
            write = False
            result = 0
        elif funct == FUNCT["jalr"]:
            self.write(rd, _u32(self.pc + WORD_BYTES))
            self._pc_next = rs
            write = False
            result = 0
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
        elif funct == FUNCT["halt"]:
            self.halted = True
            write = False
            result = 0
        else:
            raise ValueError(f"funct not implemented: {funct:#08b}")
        if write:
            self.write(rd, result)

    def step(self, word: int) -> None:
        if self.halted:
            return
        self._pc_next = None
        fields = unpack_r(word)
        opcode = fields["opcode"]
        rd, rs_i = fields["rd"], fields["rs"]
        imm16 = fields["imm16"]
        if opcode == OPCODE_SPECIAL:
            self._step_special(fields)
        elif opcode == OPCODE["addi"]:
            self.write(rd, self._alu_add(self.read(rs_i), _u32(sext16(imm16))))
        elif opcode == OPCODE["andi"]:
            self.write(rd, self._alu_logic(self.read(rs_i) & imm16))
        elif opcode == OPCODE["ori"]:
            self.write(rd, self._alu_logic(self.read(rs_i) | imm16))
        elif opcode == OPCODE["xori"]:
            self.write(rd, self._alu_logic(self.read(rs_i) ^ imm16))
        elif opcode == OPCODE["lui"]:
            self.write(rd, _u32(imm16 << 16))
        elif opcode == OPCODE["adr"]:
            self.write(rd, _u32(self.pc + WORD_BYTES + sext16(imm16)))
        elif opcode == OPCODE["lb"]:
            self._load(rd, rs_i, imm16, 1, True)
        elif opcode == OPCODE["lbu"]:
            self._load(rd, rs_i, imm16, 1, False)
        elif opcode == OPCODE["lh"]:
            self._load(rd, rs_i, imm16, 2, True)
        elif opcode == OPCODE["lhu"]:
            self._load(rd, rs_i, imm16, 2, False)
        elif opcode == OPCODE["lw"]:
            self._load(rd, rs_i, imm16, 4, False)
        elif opcode == OPCODE["sb"]:
            self._store(rd, rs_i, imm16, 1)
        elif opcode == OPCODE["sh"]:
            self._store(rd, rs_i, imm16, 2)
        elif opcode == OPCODE["sw"]:
            self._store(rd, rs_i, imm16, 4)
        elif opcode == OPCODE["j"]:
            self._jump_abs(fields["target26"])
        elif opcode == OPCODE["jal"]:
            self.write(3, _u32(self.pc + WORD_BYTES))
            self._jump_abs(fields["target26"])
        elif opcode == OPCODE["bcc"]:
            if self._branch_taken(fields["cond"]):
                self._pc_next = _u32(self.pc + WORD_BYTES + (sext22(fields["imm22"]) << 2))
        else:
            raise ValueError(f"opcode not implemented: {opcode:#08b}")
        self._force_wired()
        if self._pc_next is not None:
            self.pc = _u32(self._pc_next)
        else:
            self.pc = _u32(self.pc + WORD_BYTES)
