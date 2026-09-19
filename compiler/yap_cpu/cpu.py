"""Clocked microcoded CPU. One step() is one clock (docs/cpu/design.md)."""

from compiler.yap_cpu.control import (
    A_CSR,
    A_EPC,
    A_FOUR,
    A_JTARGET,
    A_MDR,
    A_PC,
    A_RF,
    A_ZERO,
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
    B_RT5,
    B_SHAMT,
    B_ZERO,
    DST_CSR,
    DST_FLAGS,
    DST_IR,
    DST_MAR,
    DST_MDR,
    DST_PC,
    DST_RF,
    FLAG_ADD,
    FLAG_LOGIC,
    FLAG_MULDIV,
    FLAG_SHIFT,
    FLAG_SUB,
    FLAG_TEQ,
    FLAG_TEST,
    IDX_RA,
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
    SEQ_SKIP_UNLESS,
    SEQ_TRAP,
    unpack_cw,
)
from compiler.yap_cpu.ucode import U_FETCH, build_rom, dispatch
from compiler.yap_isa.cpu import Flags
from compiler.yap_isa.csrs import CAUSE_ALIGN, CAUSE_IRQ, CAUSE_PROT, CAUSE_SYS, TRAP_VECTOR
from compiler.yap_isa.encode import sext16, sext22, unpack_r

MASK = 0xFFFFFFFF
LAT_WIRED = 0
LAT_MOSFET = 1
LAT_IC = 2
LAT_MEM = 1


def _u32(x: int) -> int:
    return x & MASK


def _sign(x: int) -> int:
    return (x >> 31) & 1


def _bank_lat(idx: int) -> int:
    if idx <= 2:
        return LAT_WIRED
    if idx <= 15:
        return LAT_MOSFET
    return LAT_IC


class Cpu:
    def __init__(self, mem_size: int = 65536):
        self.mem = bytearray(mem_size)
        self.pc = 0
        self.ir = 0
        self.upc = U_FETCH
        self.halted = False
        self.cycles = 0
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
        self.A = 0
        self.B = 0
        self.aluout = 0
        self.mar = 0
        self.mdr = 0
        self._mosfet = [0] * 13
        self._ic = [0] * 16
        self._rom = build_rom()
        self._a_wait = 0
        self._b_wait = 0
        self._w_wait = 0
        self._mem_wait = 0
        self._mem_size = 4
        self._mem_write = False
        self._mem_sext = False
        self._a_data = 0
        self._b_data = 0
        self._w_idx = 0
        self._w_val = 0
        self._pending_seq = None
        self._irq = False
        self._alu_c = 0

    @property
    def supervisor(self) -> bool:
        return self.p == 1

    def irq(self) -> None:
        self._irq = True

    def read(self, idx: int) -> int:
        if not (0 <= idx < 32):
            raise ValueError(f"register index out of range: {idx}")
        if idx == 0:
            return 0
        if idx == 1:
            return 1
        if idx == 2:
            return MASK
        if idx <= 15:
            return _u32(self._mosfet[idx - 3])
        return _u32(self._ic[idx - 16])

    def write(self, idx: int, value: int) -> None:
        if not (0 <= idx < 32):
            raise ValueError(f"register index out of range: {idx}")
        if idx <= 2:
            return
        if idx <= 15:
            self._mosfet[idx - 3] = _u32(value)
            return
        self._ic[idx - 16] = _u32(value)

    def mem_store(self, addr: int, data: bytes) -> None:
        end = addr + len(data)
        if addr < 0 or end > len(self.mem):
            raise ValueError(f"memory store out of range: {addr}")
        self.mem[addr:end] = data

    def _ir_idx(self, sel: int) -> int:
        fields = unpack_r(self.ir)
        if sel == IDX_RS:
            return fields["rs"]
        if sel == IDX_RT:
            return fields["rt"]
        if sel == IDX_RD:
            return fields["rd"]
        if sel == IDX_RA:
            return 3
        return 0

    def _busy(self) -> bool:
        return self._a_wait > 0 or self._b_wait > 0 or self._w_wait > 0 or self._mem_wait > 0

    def _tick_waits(self) -> None:
        if self._a_wait > 0:
            self._a_wait -= 1
            if self._a_wait == 0:
                self.A = self._a_data
        if self._b_wait > 0:
            self._b_wait -= 1
            if self._b_wait == 0:
                self.B = self._b_data
        if self._w_wait > 0:
            self._w_wait -= 1
            if self._w_wait == 0:
                self.write(self._w_idx, self._w_val)
        if self._mem_wait > 0:
            self._mem_wait -= 1
            if self._mem_wait == 0:
                size = self._mem_size
                addr = self.mar
                if self._mem_write:
                    val = self.mdr & ((1 << (8 * size)) - 1)
                    self.mem[addr : addr + size] = val.to_bytes(size, "little")
                else:
                    raw = int.from_bytes(self.mem[addr : addr + size], "little")
                    if self._mem_sext:
                        sign_bit = 1 << (8 * size - 1)
                        if raw & sign_bit:
                            raw -= 1 << (8 * size)
                    self.mdr = _u32(raw)

    def _do_trap(self, code: int) -> None:
        self.cause = code
        self.pie = self.ie
        self.pp = self.p
        self.p = 1
        self.ie = 0
        if code == CAUSE_SYS:
            self.epc = _u32(self.pc + 4)
        else:
            self.epc = _u32(self.pc)
        self.pc = TRAP_VECTOR
        self.upc = U_FETCH
        self._pending_seq = None
        self._irq = False

    def _a_mux(self, sel: int) -> int:
        if sel == A_RF:
            return self.A
        if sel == A_PC:
            return _u32(self.pc)
        if sel == A_EPC:
            return _u32(self.epc)
        if sel == A_MDR:
            return _u32(self.mdr)
        if sel == A_CSR:
            return 0
        if sel == A_ZERO:
            return 0
        if sel == A_FOUR:
            return 4
        if sel == A_JTARGET:
            nxt = _u32(self.pc + 4)
            return (nxt & 0xF0000000) | ((self.ir & 0x03FFFFFF) << 2)
        return 0

    def _b_mux(self, sel: int) -> int:
        fields = unpack_r(self.ir)
        if sel == B_RF:
            return self.B
        if sel == B_IMM_SE:
            return _u32(sext16(fields["imm16"]))
        if sel == B_IMM_ZE:
            return fields["imm16"] & 0xFFFF
        if sel == B_SHAMT:
            return fields["shamt"] & 31
        if sel == B_RT5:
            return fields["rt"] & 31
        if sel == B_FOUR:
            return 4
        if sel == B_ZERO:
            return 0
        if sel == B_BROFF:
            return _u32(sext22(fields["imm22"]) << 2)
        return 0

    def _alu(self, op: int, a: int, b: int) -> int:
        a, b = _u32(a), _u32(b)
        if op == ALU_ADD:
            return _u32(a + b)
        if op == ALU_SUB:
            return _u32(a - b)
        if op == ALU_AND:
            return _u32(a & b)
        if op == ALU_OR:
            return _u32(a | b)
        if op == ALU_XOR:
            return _u32(a ^ b)
        if op == ALU_NOT:
            return _u32(~a)
        if op == ALU_SLL:
            sh = b & 31
            if sh == 0:
                self._alu_c = 0
                return a
            self._alu_c = (a >> (32 - sh)) & 1
            return _u32(a << sh)
        if op == ALU_SRL:
            sh = b & 31
            if sh == 0:
                self._alu_c = 0
                return a
            self._alu_c = (a >> (sh - 1)) & 1
            return a >> sh
        if op == ALU_SRA:
            sh = b & 31
            signed = a - 0x100000000 if _sign(a) else a
            if sh == 0:
                self._alu_c = 0
            else:
                self._alu_c = (a >> (sh - 1)) & 1
            return _u32(signed >> sh)
        if op == ALU_MUL:
            return _u32(a * b)
        if op == ALU_DIV:
            return 0 if b == 0 else _u32(a // b)
        if op == ALU_PASS_A:
            return a
        if op == ALU_PASS_B:
            return b
        if op == ALU_LUI:
            return _u32((unpack_r(self.ir)["imm16"] & 0xFFFF) << 16)
        return a

    def _set_flags(self, mode: int, a: int, b: int, result: int) -> None:
        a, b, result = _u32(a), _u32(b), _u32(result)
        if mode == FLAG_ADD:
            self.flags.c = int((a + b) > MASK)
            self.flags.v = int(_sign(a) == _sign(b) and _sign(result) != _sign(a))
            self.flags.set_zn(result)
            return
        if mode == FLAG_SUB:
            self.flags.c = int(a < b)
            self.flags.v = int(_sign(a) != _sign(b) and _sign(result) != _sign(a))
            self.flags.set_zn(result)
            return
        if mode == FLAG_LOGIC:
            self.flags.c = 0
            self.flags.v = 0
            self.flags.set_zn(result)
            return
        if mode == FLAG_SHIFT:
            self.flags.c = self._alu_c
            self.flags.v = 0
            self.flags.set_zn(result)
            return
        if mode == FLAG_TEQ:
            self.flags.z = int(result == 0)
            self.flags.n = 0
            self.flags.c = 0
            self.flags.v = 0
            return
        if mode == FLAG_TEST:
            self.flags.c = 0
            self.flags.v = 0
            self.flags.set_zn(result)
            return
        if mode == FLAG_MULDIV:
            self.flags.c = 0
            self.flags.v = 0
            self.flags.set_zn(result)

    def _apply_seq(self, seq: int, uimm: int) -> None:
        if seq == SEQ_NEXT:
            self.upc = (self.upc + 1) & 0xFF
        elif seq == SEQ_DISPATCH:
            self.upc = dispatch(self.ir) & 0xFF
        elif seq == SEQ_GOTO:
            self.upc = uimm & 0xFF
        elif seq == SEQ_HALT:
            self.halted = True
        elif seq == SEQ_TRAP:
            self._do_trap(uimm)
        elif seq == SEQ_ERET:
            self.ie = self.pie
            self.p = self.pp
            self.pc = _u32(self.epc)
            self.upc = U_FETCH
        elif seq in (SEQ_SKIP_IF, SEQ_SKIP_UNLESS):
            self.upc = (self.upc + 1) & 0xFF

    def _in_window(self, addr: int, size: int) -> bool:
        last = addr + size - 1
        return self.ubase <= addr and last < self.ulimit

    def _mem_ok(self, addr: int, size: int) -> bool:
        if size > 1 and addr % size != 0:
            self._do_trap(CAUSE_ALIGN)
            return False
        if not self.supervisor and not self._in_window(addr, size):
            self._do_trap(CAUSE_PROT)
            return False
        return True

    def _execute_cw(self, cw) -> None:
        if cw.irq_chk and self.ie and self._irq:
            self._do_trap(CAUSE_IRQ)
            return
        if cw.irq_chk:
            if self.pc % 4 != 0:
                self._do_trap(CAUSE_ALIGN)
                return
            if not self.supervisor and not self._in_window(self.pc, 4):
                self._do_trap(CAUSE_PROT)
                return

        if cw.re_a:
            idx = self._ir_idx(cw.idx_a)
            self._a_data = self.read(idx)
            lat = _bank_lat(idx)
            if lat == 0:
                self.A = self._a_data
            else:
                self._a_wait = lat
        if cw.re_b:
            idx = self._ir_idx(cw.idx_b)
            self._b_data = self.read(idx)
            lat = _bank_lat(idx)
            if lat == 0:
                self.B = self._b_data
            else:
                self._b_wait = lat

        a = self._a_mux(cw.a_sel)
        b = self._b_mux(cw.b_sel)
        self.aluout = self._alu(cw.alu_op, a, b)
        if cw.we_flags:
            self._set_flags(cw.flag_mode, a, b, self.aluout)

        if cw.dst == DST_MAR:
            self.mar = _u32(self.aluout)
        elif cw.dst == DST_MDR:
            self.mdr = _u32(self.aluout)
        elif cw.dst == DST_IR:
            self.ir = _u32(self.aluout)
        elif cw.dst == DST_PC:
            self.pc = _u32(self.aluout)
        elif cw.dst == DST_FLAGS:
            self.flags.z = self.aluout & 1
            self.flags.n = (self.aluout >> 1) & 1
            self.flags.c = (self.aluout >> 2) & 1
            self.flags.v = (self.aluout >> 3) & 1

        if cw.we_pc:
            self.pc = _u32(self.aluout)
        if cw.we_ir:
            self.ir = _u32(self.mdr)

        if cw.we_rf:
            rd = unpack_r(self.ir)["rd"]
            if rd <= 2:
                pass
            else:
                lat = _bank_lat(rd)
                self._w_idx = rd
                self._w_val = self.aluout
                if lat == 0:
                    self.write(rd, self.aluout)
                else:
                    self._w_wait = lat

        if cw.mem_re or cw.mem_we:
            size = {MEM_BYTE: 1, MEM_HALF: 2, MEM_WORD: 4}.get(cw.mem_sz, 4)
            if not self._mem_ok(self.mar, size):
                return
            self._mem_wait = LAT_MEM
            self._mem_size = size
            self._mem_write = bool(cw.mem_we)
            self._mem_sext = bool(cw.load_sext)

        if cw.seq == SEQ_HALT:
            self.halted = True
            return
        if cw.seq == SEQ_TRAP:
            self._do_trap(cw.uimm)
            return
        if self._busy():
            self._pending_seq = (cw.seq, cw.uimm)
            return
        self._apply_seq(cw.seq, cw.uimm)

    def step(self) -> None:
        if self.halted:
            return
        self.cycles += 1
        if self._busy():
            self._tick_waits()
            if self._busy():
                return
            if self._pending_seq is not None:
                seq, uimm = self._pending_seq
                self._pending_seq = None
                self._apply_seq(seq, uimm)
            return
        cw = unpack_cw(self._rom[self.upc])
        self._execute_cw(cw)

    def run(self, max_cycles: int = 100000) -> None:
        for _ in range(max_cycles):
            if self.halted:
                return
            self.step()
