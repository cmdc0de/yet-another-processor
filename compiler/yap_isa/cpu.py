"""Behavioral model: GPRs, FLAGS, memory, DIV, load/store, jumps."""

from compiler.yap_isa.csrs import (
    CAUSE_ALIGN,
    CAUSE_COP,
    CAUSE_IRQ,
    CAUSE_PAGE_FAULT,
    CAUSE_PRIV,
    CAUSE_PROT,
    CAUSE_SYS,
    CAUSE_TLB_MISS,
    COP0_MFC0,
    COP0_MTC0,
    COP1_MFC1,
    COP1_MTC1,
    CSR_CAUSE,
    CSR_EPC,
    CSR_FLAGS,
    CSR_STATUS,
    CSR_UBASE,
    CSR_ULIMIT,
    STATUS_IE,
    STATUS_P,
    STATUS_PIE,
    STATUS_PP,
    STATUS_TE,
    TRAP_VECTOR,
)
from compiler.yap_isa.encode import COND, FUNCT, OPCODE, OPCODE_SPECIAL, sext16, sext22, unpack_r

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
    def __init__(self, mem_size: int = 65536):
        self._gprs = [0] * 32
        self.pc = 0
        self.flags = Flags()
        self.cause = 0
        self.epc = 0
        self.ie = 0
        self.p = 1
        self.te = 0
        self.pie = 0
        self.pp = 1
        self.ubase = 0
        self.ulimit = mem_size
        self.fregs = [0] * 32
        self.mem = bytearray(mem_size)
        self.halted = False
        self._pc_next = None
        self._force_wired()

    @property
    def supervisor(self) -> bool:
        return self.p == 1

    def status_word(self) -> int:
        return (
            (self.ie & 1)
            | ((self.p & 1) << STATUS_P)
            | ((self.te & 1) << STATUS_TE)
            | ((self.pie & 1) << STATUS_PIE)
            | ((self.pp & 1) << STATUS_PP)
        )

    def flags_word(self) -> int:
        f = self.flags
        return (f.z & 1) | ((f.n & 1) << 1) | ((f.c & 1) << 2) | ((f.v & 1) << 3)

    def _set_flags_word(self, value: int) -> None:
        self.flags.z = value & 1
        self.flags.n = (value >> 1) & 1
        self.flags.c = (value >> 2) & 1
        self.flags.v = (value >> 3) & 1

    def _in_window(self, addr: int, size: int) -> bool:
        last = addr + size - 1
        return self.ubase <= addr and last < self.ulimit

    def _trap(self, code, epc=None) -> None:
        self.cause = code
        self.pie = self.ie
        self.pp = self.p
        self.p = 1
        self.ie = 0
        self.epc = self.pc if epc is None else _u32(epc)
        self._pc_next = TRAP_VECTOR

    def irq(self) -> None:
        if self.halted or not self.ie:
            return
        self._trap(CAUSE_IRQ, epc=self.pc)
        self.pc = _u32(self._pc_next)
        self._pc_next = None

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
            self._trap(CAUSE_ALIGN)
            return False
        return True

    def _check_user_addr(self, addr: int, size: int) -> bool:
        if not self.supervisor and not self._in_window(addr, size):
            self._trap(CAUSE_PROT)
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
        if not self._check_user_addr(addr, size):
            return
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
        if not self._check_user_addr(addr, size):
            return
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
        elif funct == FUNCT["eret"]:
            write = False
            result = 0
            if not self.supervisor:
                self._trap(CAUSE_PRIV)
            else:
                self.ie = self.pie
                self.p = self.pp
                self._pc_next = self.epc
        else:
            raise ValueError(f"funct not implemented: {funct:#08b}")
        if write:
            self.write(rd, result)

    def _read_csr(self, index: int) -> int:
        if index == CSR_STATUS:
            return self.status_word()
        if index == CSR_FLAGS:
            return self.flags_word()
        if index == CSR_EPC:
            return _u32(self.epc)
        if index == CSR_CAUSE:
            return _u32(self.cause)
        if index == CSR_UBASE:
            return _u32(self.ubase)
        if index == CSR_ULIMIT:
            return _u32(self.ulimit)
        return 0

    def _write_csr(self, index: int, value: int) -> None:
        value = _u32(value)
        if index == CSR_STATUS:
            if (value >> STATUS_TE) & 1:
                self._trap(CAUSE_PRIV)
                return
            self.ie = value & 1
            self.p = (value >> STATUS_P) & 1
            self.te = 0
            self.pie = (value >> STATUS_PIE) & 1
            self.pp = (value >> STATUS_PP) & 1
            return
        if index == CSR_FLAGS:
            self._set_flags_word(value)
            return
        if index == CSR_EPC:
            self.epc = value
            return
        if index == CSR_CAUSE:
            self.cause = value
            return
        if index == CSR_UBASE:
            self.ubase = value
            return
        if index == CSR_ULIMIT:
            self.ulimit = value

    def _step_cop0(self, fields: dict) -> None:
        rd, rs, csr = fields["rd"], fields["rs"], fields["rt"]
        user_ok_read = csr in (CSR_STATUS, CSR_FLAGS)
        if rs == COP0_MFC0:
            if not self.supervisor and not user_ok_read:
                self._trap(CAUSE_PRIV)
                return
            self.write(rd, self._read_csr(csr))
            return
        if rs == COP0_MTC0:
            if not self.supervisor:
                self._trap(CAUSE_PRIV)
                return
            self._write_csr(csr, self.read(rd))
            return
        self._trap(CAUSE_PRIV)

    def read_f(self, idx: int) -> int:
        if not (0 <= idx < 32):
            raise ValueError(f"fp register out of range: {idx}")
        return self.fregs[idx] & MASK

    def write_f(self, idx: int, value: int) -> None:
        if not (0 <= idx < 32):
            raise ValueError(f"fp register out of range: {idx}")
        self.fregs[idx] = value & MASK

    def _step_cop1(self, fields: dict) -> None:
        rd, rs, fs = fields["rd"], fields["rs"], fields["rt"]
        if rs == COP1_MFC1:
            self.write(rd, self.read_f(fs))
            return
        if rs == COP1_MTC1:
            self.write_f(fs, self.read(rd))
            return
        self._trap(CAUSE_COP)

    def step(self, word: int) -> None:
        if self.halted:
            return
        self._pc_next = None
        if self.pc % WORD_BYTES != 0:
            self._trap(CAUSE_ALIGN)
        elif not self.supervisor and not self._in_window(self.pc, WORD_BYTES):
            self._trap(CAUSE_PROT)
        if self._pc_next is not None:
            self.pc = _u32(self._pc_next)
            return
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
        elif opcode == OPCODE["sys"]:
            self._trap(CAUSE_SYS, epc=self.pc + WORD_BYTES)
        elif opcode == OPCODE["cop0"]:
            self._step_cop0(fields)
        elif opcode == OPCODE["cop1"]:
            self._step_cop1(fields)
        else:
            raise ValueError(f"opcode not implemented: {opcode:#08b}")
        self._force_wired()
        if self._pc_next is not None:
            self.pc = _u32(self._pc_next)
        else:
            self.pc = _u32(self.pc + WORD_BYTES)
