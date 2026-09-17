//! CPU: little-endian SRAM, PC, halt, GPRs, FLAGS, integer ALU, memory, jumps (m1–m4).

use crate::yap1::Yap1;

pub const DEFAULT_MEM: usize = 65536;
pub const DEFAULT_MAX_STEPS: u32 = 100_000;
pub const HALT_WORD: u32 = 0x0000_002C;
pub const MASK: u32 = 0xFFFF_FFFF;
pub const T0: usize = 10;
pub const T1: usize = 11;
pub const RA: usize = 3;
pub const CAUSE_ALIGN: u32 = 8;
pub const TRAP_VECTOR: u32 = 0x80;

const OPCODE_SPECIAL: u32 = 0;
const OPCODE_J: u32 = 0b000010;
const OPCODE_JAL: u32 = 0b000011;
const OPCODE_BCC: u32 = 0b000100;
const OPCODE_ADDI: u32 = 0b001000;
const OPCODE_ADR: u32 = 0b001001;
const OPCODE_ANDI: u32 = 0b001100;
const OPCODE_ORI: u32 = 0b001101;
const OPCODE_XORI: u32 = 0b001110;
const OPCODE_LUI: u32 = 0b001111;
const OPCODE_LB: u32 = 0b100000;
const OPCODE_LH: u32 = 0b100001;
const OPCODE_LW: u32 = 0b100011;
const OPCODE_LBU: u32 = 0b100100;
const OPCODE_LHU: u32 = 0b100101;
const OPCODE_SB: u32 = 0b101000;
const OPCODE_SH: u32 = 0b101001;
const OPCODE_SW: u32 = 0b101011;
const FUNCT_SLL: u32 = 0b000000;
const FUNCT_SRL: u32 = 0b000010;
const FUNCT_SRA: u32 = 0b000011;
const FUNCT_SLLV: u32 = 0b000100;
const FUNCT_SRLV: u32 = 0b000110;
const FUNCT_SRAV: u32 = 0b000111;
const FUNCT_JR: u32 = 0b001000;
const FUNCT_JALR: u32 = 0b001001;
const FUNCT_MUL: u32 = 0b011000;
const FUNCT_DIV: u32 = 0b011010;
const FUNCT_ADD: u32 = 0b100000;
const FUNCT_SUB: u32 = 0b100010;
const FUNCT_AND: u32 = 0b100100;
const FUNCT_OR: u32 = 0b100101;
const FUNCT_XOR: u32 = 0b100110;
const FUNCT_NOT: u32 = 0b100111;
const FUNCT_TEST: u32 = 0b101000;
const FUNCT_TEQ: u32 = 0b101001;
const FUNCT_CMP: u32 = 0b101010;
const FUNCT_HALT: u32 = 0b101100;

const COND_EQ: u32 = 0;
const COND_NE: u32 = 1;
const COND_LT: u32 = 2;
const COND_GE: u32 = 3;
const COND_LO: u32 = 4;
const COND_HS: u32 = 5;
const COND_LE: u32 = 6;
const COND_GT: u32 = 7;
const COND_MI: u32 = 8;
const COND_PL: u32 = 9;

#[derive(Debug, Clone, Copy, Default, PartialEq, Eq)]
pub struct Flags {
    pub z: u8,
    pub n: u8,
    pub c: u8,
    pub v: u8,
}

#[derive(Debug)]
pub struct Cpu {
    pub mem: Vec<u8>,
    pub pc: u32,
    pub halted: bool,
    gprs: [u32; 32],
    pub flags: Flags,
    pub cause: u32,
    pc_next: Option<u32>,
}

impl Cpu {
    pub fn new(mem_size: usize) -> Self {
        Self {
            mem: vec![0; mem_size],
            pc: 0,
            halted: false,
            gprs: [0; 32],
            flags: Flags::default(),
            cause: 0,
            pc_next: None,
        }
    }

    pub fn from_image(image: &Yap1) -> Result<Self, String> {
        let end = (image.load as u64)
            .checked_add(image.payload.len() as u64)
            .ok_or_else(|| "image does not fit in address space".to_string())?;
        let need = end.max(u64::from(image.entry) + 4).max(DEFAULT_MEM as u64);
        if need > usize::MAX as u64 {
            return Err("image does not fit in host memory".into());
        }
        let mut cpu = Self::new(need as usize);
        cpu.load_image(image)?;
        Ok(cpu)
    }

    pub fn load_image(&mut self, image: &Yap1) -> Result<(), String> {
        let start = image.load as usize;
        let end = start
            .checked_add(image.payload.len())
            .ok_or_else(|| "image does not fit in address space".to_string())?;
        if end > self.mem.len() {
            self.mem.resize(end, 0);
        }
        if !image.payload.is_empty() {
            self.mem[start..end].copy_from_slice(&image.payload);
        }
        self.pc = image.entry;
        self.halted = false;
        self.pc_next = None;
        Ok(())
    }

    pub fn read(&self, idx: usize) -> u32 {
        match idx {
            0 => 0,
            1 => 1,
            2 => MASK,
            3..=31 => self.gprs[idx],
            _ => panic!("register index out of range: {idx}"),
        }
    }

    pub fn write(&mut self, idx: usize, value: u32) {
        if idx <= 2 || idx >= 32 {
            return;
        }
        self.gprs[idx] = value;
    }

    pub fn mem_load(&self, addr: u32, size: usize) -> Result<&[u8], String> {
        let start = addr as usize;
        let end = start
            .checked_add(size)
            .ok_or_else(|| "memory load out of range".to_string())?;
        if end > self.mem.len() {
            return Err("memory load out of range".into());
        }
        Ok(&self.mem[start..end])
    }

    pub fn mem_store(&mut self, addr: u32, data: &[u8]) -> Result<(), String> {
        let start = addr as usize;
        let end = start
            .checked_add(data.len())
            .ok_or_else(|| "memory store out of range".to_string())?;
        if end > self.mem.len() {
            return Err("memory store out of range".into());
        }
        self.mem[start..end].copy_from_slice(data);
        Ok(())
    }

    pub fn fetch_u32(&self, addr: u32) -> Result<u32, String> {
        let bytes = self.mem_load(addr, 4)?;
        Ok(u32::from_le_bytes(bytes.try_into().unwrap()))
    }

    pub fn is_halt_word(word: u32) -> bool {
        let opcode = (word >> 26) & 0x3F;
        let funct = word & 0x3F;
        opcode == OPCODE_SPECIAL && funct == FUNCT_HALT
    }

    fn sign(x: u32) -> u8 {
        ((x >> 31) & 1) as u8
    }

    fn set_zn(&mut self, result: u32) {
        self.flags.z = u8::from(result == 0);
        self.flags.n = Self::sign(result);
    }

    fn set_zncv_add(&mut self, rs: u32, rt: u32, result: u32, carry: u8) {
        self.flags.c = carry;
        self.flags.v =
            u8::from(Self::sign(rs) == Self::sign(rt) && Self::sign(result) != Self::sign(rs));
        self.set_zn(result);
    }

    fn set_zncv_sub(&mut self, rs: u32, rt: u32, result: u32) {
        self.flags.c = u8::from(rs < rt);
        self.flags.v =
            u8::from(Self::sign(rs) != Self::sign(rt) && Self::sign(result) != Self::sign(rs));
        self.set_zn(result);
    }

    fn alu_add(&mut self, rs: u32, rt: u32) -> u32 {
        let raw = rs as u64 + rt as u64;
        let result = raw as u32;
        self.set_zncv_add(rs, rt, result, u8::from(raw > u64::from(MASK)));
        result
    }

    fn alu_sub(&mut self, rs: u32, rt: u32) -> u32 {
        let result = rs.wrapping_sub(rt);
        self.set_zncv_sub(rs, rt, result);
        result
    }

    fn alu_logic(&mut self, result: u32) -> u32 {
        self.flags.c = 0;
        self.flags.v = 0;
        self.set_zn(result);
        result
    }

    fn alu_sll(&mut self, rs: u32, shamt: u32) -> u32 {
        let shamt = shamt & 31;
        let (c, result) = if shamt == 0 {
            (0, rs)
        } else {
            (((rs >> (32 - shamt)) & 1) as u8, rs.wrapping_shl(shamt))
        };
        self.flags.c = c;
        self.flags.v = 0;
        self.set_zn(result);
        result
    }

    fn alu_srl(&mut self, rs: u32, shamt: u32) -> u32 {
        let shamt = shamt & 31;
        let (c, result) = if shamt == 0 {
            (0, rs)
        } else {
            (((rs >> (shamt - 1)) & 1) as u8, rs >> shamt)
        };
        self.flags.c = c;
        self.flags.v = 0;
        self.set_zn(result);
        result
    }

    fn alu_sra(&mut self, rs: u32, shamt: u32) -> u32 {
        let shamt = shamt & 31;
        let c = if shamt == 0 {
            0
        } else {
            ((rs >> (shamt - 1)) & 1) as u8
        };
        let result = ((rs as i32) >> shamt) as u32;
        self.flags.c = c;
        self.flags.v = 0;
        self.set_zn(result);
        result
    }

    fn alu_mul(&mut self, rs: u32, rt: u32) -> u32 {
        let result = rs.wrapping_mul(rt);
        self.flags.c = 0;
        self.flags.v = 0;
        self.set_zn(result);
        result
    }

    fn alu_div(&mut self, rs: u32, rt: u32) -> u32 {
        let result = if rt == 0 { 0 } else { rs / rt };
        self.flags.c = 0;
        self.flags.v = 0;
        self.set_zn(result);
        result
    }

    fn sext16(imm16: u32) -> u32 {
        let imm16 = imm16 & 0xFFFF;
        if imm16 & 0x8000 != 0 {
            imm16 | 0xFFFF_0000
        } else {
            imm16
        }
    }

    fn sext22(imm22: u32) -> i32 {
        let imm22 = imm22 & 0x3F_FFFF;
        if imm22 & 0x20_0000 != 0 {
            imm22 as i32 - 0x40_0000
        } else {
            imm22 as i32
        }
    }

    fn trap_align(&mut self) {
        self.cause = CAUSE_ALIGN;
        self.pc_next = Some(TRAP_VECTOR);
    }

    fn addr(&self, rs: u32, imm16: u32) -> u32 {
        rs.wrapping_add(Self::sext16(imm16))
    }

    fn load(&mut self, rd: usize, rs: u32, imm16: u32, size: usize, signed: bool) {
        let addr = self.addr(rs, imm16);
        if addr % size as u32 != 0 {
            self.trap_align();
            return;
        }
        let Ok(bytes) = self.mem_load(addr, size) else {
            return;
        };
        let mut raw = 0u32;
        for (i, b) in bytes.iter().enumerate() {
            raw |= u32::from(*b) << (8 * i);
        }
        if signed {
            let bits = size * 8;
            let sign = 1u32 << (bits - 1);
            if raw & sign != 0 {
                raw |= MASK << bits;
            }
        }
        self.write(rd, raw);
    }

    fn store(&mut self, rd: usize, rs: u32, imm16: u32, size: usize) {
        let addr = self.addr(rs, imm16);
        if addr % size as u32 != 0 {
            self.trap_align();
            return;
        }
        let value = self.read(rd);
        let mut data = [0u8; 4];
        for i in 0..size {
            data[i] = ((value >> (8 * i)) & 0xFF) as u8;
        }
        let _ = self.mem_store(addr, &data[..size]);
    }

    fn jump_abs(&mut self, target26: u32) {
        let next = self.pc.wrapping_add(4);
        self.pc_next = Some((next & 0xF000_0000) | ((target26 & 0x03FF_FFFF) << 2));
    }

    fn branch_taken(&self, cond: u32) -> bool {
        let (z, n, c, v) = (
            self.flags.z != 0,
            self.flags.n != 0,
            self.flags.c != 0,
            self.flags.v != 0,
        );
        let nv = n ^ v;
        match cond {
            COND_EQ => z,
            COND_NE => !z,
            COND_LT => nv,
            COND_GE => !nv,
            COND_LO => c,
            COND_HS => !c,
            COND_LE => z || nv,
            COND_GT => !(z || nv),
            COND_MI => n,
            COND_PL => !n,
            _ => false,
        }
    }

    fn execute(&mut self, word: u32) {
        let opcode = (word >> 26) & 0x3F;
        let rd = ((word >> 21) & 0x1F) as usize;
        let rs_i = ((word >> 16) & 0x1F) as usize;
        let rt_i = ((word >> 11) & 0x1F) as usize;
        let shamt = (word >> 6) & 0x1F;
        let funct = word & 0x3F;
        let imm16 = word & 0xFFFF;
        let rs = self.read(rs_i);
        let rt = self.read(rt_i);
        if opcode == OPCODE_SPECIAL {
            let (result, write) = match funct {
                FUNCT_ADD => (self.alu_add(rs, rt), true),
                FUNCT_SUB => (self.alu_sub(rs, rt), true),
                FUNCT_AND => (self.alu_logic(rs & rt), true),
                FUNCT_OR => (self.alu_logic(rs | rt), true),
                FUNCT_XOR => (self.alu_logic(rs ^ rt), true),
                FUNCT_NOT => (self.alu_logic(!rs), true),
                FUNCT_SLL => (self.alu_sll(rs, shamt), true),
                FUNCT_SRL => (self.alu_srl(rs, shamt), true),
                FUNCT_SRA => (self.alu_sra(rs, shamt), true),
                FUNCT_SLLV => (self.alu_sll(rs, rt & 31), true),
                FUNCT_SRLV => (self.alu_srl(rs, rt & 31), true),
                FUNCT_SRAV => (self.alu_sra(rs, rt & 31), true),
                FUNCT_MUL => (self.alu_mul(rs, rt), true),
                FUNCT_DIV => (self.alu_div(rs, rt), true),
                FUNCT_JR => {
                    self.pc_next = Some(rs);
                    (0, false)
                }
                FUNCT_JALR => {
                    self.write(rd, self.pc.wrapping_add(4));
                    self.pc_next = Some(rs);
                    (0, false)
                }
                FUNCT_CMP => {
                    self.alu_sub(rs, rt);
                    (0, false)
                }
                FUNCT_TEST => {
                    self.alu_logic(rs & rt);
                    (0, false)
                }
                FUNCT_TEQ => {
                    let result = rs ^ rt;
                    self.flags.z = u8::from(result == 0);
                    self.flags.n = 0;
                    self.flags.c = 0;
                    self.flags.v = 0;
                    (0, false)
                }
                FUNCT_HALT => {
                    self.halted = true;
                    (0, false)
                }
                _ => (0, false),
            };
            if write {
                self.write(rd, result);
            }
            return;
        }
        match opcode {
            OPCODE_ADDI => {
                let result = self.alu_add(rs, Self::sext16(imm16));
                self.write(rd, result);
            }
            OPCODE_ANDI => {
                let result = self.alu_logic(rs & imm16);
                self.write(rd, result);
            }
            OPCODE_ORI => {
                let result = self.alu_logic(rs | imm16);
                self.write(rd, result);
            }
            OPCODE_XORI => {
                let result = self.alu_logic(rs ^ imm16);
                self.write(rd, result);
            }
            OPCODE_LUI => {
                self.write(rd, imm16 << 16);
            }
            OPCODE_ADR => {
                self.write(
                    rd,
                    self.pc.wrapping_add(4).wrapping_add(Self::sext16(imm16)),
                );
            }
            OPCODE_LB => self.load(rd, rs, imm16, 1, true),
            OPCODE_LBU => self.load(rd, rs, imm16, 1, false),
            OPCODE_LH => self.load(rd, rs, imm16, 2, true),
            OPCODE_LHU => self.load(rd, rs, imm16, 2, false),
            OPCODE_LW => self.load(rd, rs, imm16, 4, false),
            OPCODE_SB => self.store(rd, rs, imm16, 1),
            OPCODE_SH => self.store(rd, rs, imm16, 2),
            OPCODE_SW => self.store(rd, rs, imm16, 4),
            OPCODE_J => self.jump_abs(word & 0x03FF_FFFF),
            OPCODE_JAL => {
                self.write(RA, self.pc.wrapping_add(4));
                self.jump_abs(word & 0x03FF_FFFF);
            }
            OPCODE_BCC => {
                let cond = (word >> 22) & 0xF;
                let imm22 = word & 0x3F_FFFF;
                if self.branch_taken(cond) {
                    let off = (Self::sext22(imm22) << 2) as u32;
                    self.pc_next = Some(self.pc.wrapping_add(4).wrapping_add(off));
                }
            }
            _ => {}
        }
    }

    fn finish_step(&mut self) {
        self.pc = self.pc_next.unwrap_or(self.pc.wrapping_add(4));
        self.pc_next = None;
    }

    pub fn step_word(&mut self, word: u32) {
        if self.halted {
            return;
        }
        self.pc_next = None;
        if self.pc % 4 != 0 {
            self.trap_align();
            self.finish_step();
            return;
        }
        self.execute(word);
        self.finish_step();
    }

    pub fn step(&mut self) -> Result<(), String> {
        if self.halted {
            return Ok(());
        }
        self.pc_next = None;
        if self.pc % 4 != 0 {
            self.trap_align();
            self.finish_step();
            return Ok(());
        }
        let word = self.fetch_u32(self.pc)?;
        self.execute(word);
        self.finish_step();
        Ok(())
    }

    /// Run until halt or `max_steps`. Returns true if halted.
    pub fn run(&mut self, max_steps: u32) -> bool {
        for _ in 0..max_steps {
            if self.halted {
                return true;
            }
            if self.step().is_err() {
                return self.halted;
            }
        }
        self.halted
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    use crate::yap1::{pack, unpack, Yap1};

    fn halt_payload() -> Vec<u8> {
        HALT_WORD.to_le_bytes().to_vec()
    }

    fn pack_r(rd: u32, rs: u32, rt: u32, shamt: u32, funct: u32) -> u32 {
        (rd << 21) | (rs << 16) | (rt << 11) | (shamt << 6) | funct
    }

    fn pack_i(opcode: u32, rd: u32, rs: u32, imm16: u32) -> u32 {
        (opcode << 26) | (rd << 21) | (rs << 16) | (imm16 & 0xFFFF)
    }

    fn pack_j(opcode: u32, target26: u32) -> u32 {
        (opcode << 26) | (target26 & 0x03FF_FFFF)
    }

    fn pack_b(cond: u32, imm22: u32) -> u32 {
        (OPCODE_BCC << 26) | ((cond & 0xF) << 22) | (imm22 & 0x3F_FFFF)
    }

    fn bcc_to(pc: u32, cond: u32, target: u32) -> u32 {
        let next = pc.wrapping_add(4);
        let delta = target.wrapping_sub(next) as i32;
        pack_b(cond, ((delta >> 2) as u32) & 0x3F_FFFF)
    }

    fn add(rd: u32, rs: u32, rt: u32) -> u32 {
        pack_r(rd, rs, rt, 0, FUNCT_ADD)
    }

    #[test]
    fn test_emu_rust_003() {
        let image = Yap1 {
            load: 0,
            entry: 0,
            payload: halt_payload(),
        };
        let bytes = pack(&image);
        assert_eq!(&bytes[0..4], b"YAP1");
        let loaded = unpack(&bytes).unwrap();
        let cpu = Cpu::from_image(&loaded).unwrap();
        assert_eq!(&cpu.mem[0..4], halt_payload());
        assert_ne!(&cpu.mem[0..4], b"YAP1");
        assert_eq!(cpu.pc, 0);
    }

    #[test]
    fn test_emu_rust_011() {
        let word = 0x1234_5678u32;
        let image = Yap1 {
            load: 0,
            entry: 0,
            payload: word.to_le_bytes().to_vec(),
        };
        let cpu = Cpu::from_image(&image).unwrap();
        assert_eq!(&cpu.mem[0..4], &[0x78, 0x56, 0x34, 0x12]);
    }

    #[test]
    fn test_emu_rust_023() {
        let image = Yap1 {
            load: 0,
            entry: 0,
            payload: halt_payload(),
        };
        let mut cpu = Cpu::from_image(&image).unwrap();
        cpu.step().unwrap();
        assert!(cpu.halted);
        let pc = cpu.pc;
        cpu.step().unwrap();
        assert!(cpu.halted);
        assert_eq!(cpu.pc, pc);
    }

    #[test]
    fn test_emu_rust_004_run() {
        let halt = Yap1 {
            load: 0,
            entry: 0,
            payload: halt_payload(),
        };
        let mut cpu = Cpu::from_image(&halt).unwrap();
        assert!(cpu.run(DEFAULT_MAX_STEPS));

        let zeros = Yap1 {
            load: 0,
            entry: 0,
            payload: vec![0; 16],
        };
        let mut cpu = Cpu::from_image(&zeros).unwrap();
        assert!(!cpu.run(10));
    }

    #[test]
    fn test_emu_rust_013() {
        let mut cpu = Cpu::new(DEFAULT_MEM);
        assert_eq!(cpu.read(0), 0);
        assert_eq!(cpu.read(1), 1);
        assert_eq!(cpu.read(2), MASK);
        cpu.step_word(add(T0 as u32, 1, 1));
        assert_eq!(cpu.read(T0), 2);
        cpu.write(0, 99);
        assert_eq!(cpu.read(0), 0);
        cpu.step_word(add(0, 1, 1));
        assert_eq!(cpu.read(0), 0);
        assert_eq!(cpu.flags.z, 0);
    }

    #[test]
    fn test_emu_rust_014() {
        let mut cpu = Cpu::new(DEFAULT_MEM);
        cpu.step_word(add(T0 as u32, 1, 2));
        assert_eq!(cpu.read(T0), 0);
        assert_eq!(cpu.flags.z, 1);
        assert_eq!(cpu.flags.c, 1);
        cpu.step_word(pack_r(T0 as u32, 0, 1, 0, FUNCT_SUB));
        assert_eq!(cpu.read(T0), MASK);
        assert_eq!(cpu.flags.n, 1);
        assert_eq!(cpu.flags.c, 1);
    }

    #[test]
    fn test_emu_rust_015() {
        assert_eq!(pack_r(0, 0, 0, 0, FUNCT_SLL), 0);

        let mut cpu = Cpu::new(DEFAULT_MEM);
        cpu.step_word(pack_r(T0 as u32, 2, 1, 0, FUNCT_AND));
        assert_eq!(cpu.read(T0), 1);

        cpu.step_word(pack_r(T0 as u32, 0, 1, 0, FUNCT_OR));
        assert_eq!(cpu.read(T0), 1);

        cpu.step_word(pack_r(T0 as u32, 2, 2, 0, FUNCT_XOR));
        assert_eq!(cpu.read(T0), 0);

        cpu.step_word(pack_r(T0 as u32, 0, 0, 0, FUNCT_NOT));
        assert_eq!(cpu.read(T0), MASK);

        cpu.step_word(pack_r(T0 as u32, 1, 0, 3, FUNCT_SLL));
        assert_eq!(cpu.read(T0), 8);

        cpu.step_word(add(T0 as u32, 1, 1));
        cpu.step_word(pack_r(0, T0 as u32, 1, 0, FUNCT_CMP));
        assert_eq!(cpu.read(T0), 2);
        assert_eq!(cpu.flags.z, 0);
        assert_eq!(cpu.flags.c, 0);
        assert_eq!(cpu.flags.n, 0);
        cpu.step_word(pack_r(0, 1, T0 as u32, 0, FUNCT_CMP));
        assert_eq!(cpu.read(T0), 2);
        assert_eq!(cpu.flags.c, 1);

        cpu.step_word(pack_r(0, T0 as u32, 1, 0, FUNCT_TEST));
        assert_eq!(cpu.read(T0), 2);
        assert_eq!(cpu.flags.z, 1);
        assert_eq!(cpu.flags.n, 0);
        assert_eq!(cpu.flags.c, 0);
        assert_eq!(cpu.flags.v, 0);

        cpu.step_word(pack_r(0, T0 as u32, T0 as u32, 0, FUNCT_TEQ));
        assert_eq!(cpu.read(T0), 2);
        assert_eq!(cpu.flags.z, 1);
        assert_eq!(cpu.flags.n, 0);
        cpu.step_word(pack_r(0, T0 as u32, 1, 0, FUNCT_TEQ));
        assert_eq!(cpu.read(T0), 2);
        assert_eq!(cpu.flags.z, 0);
    }

    #[test]
    fn test_emu_rust_016() {
        let mut cpu = Cpu::new(DEFAULT_MEM);
        cpu.step_word(pack_r(T0 as u32, 1, 0, 3, FUNCT_SLL));
        cpu.step_word(pack_r(T0 as u32, T0 as u32, 0, 2, FUNCT_SRL));
        assert_eq!(cpu.read(T0), 2);
        cpu.step_word(pack_r(T0 as u32, T0 as u32, 1, 0, FUNCT_SRLV));
        assert_eq!(cpu.read(T0), 1);

        cpu.step_word(pack_i(OPCODE_LUI, T0 as u32, 0, 0x8000));
        assert_eq!(cpu.read(T0), 0x8000_0000);
        cpu.step_word(pack_r(T0 as u32, T0 as u32, 0, 1, FUNCT_SRA));
        assert_eq!(cpu.read(T0), 0xC000_0000);
        assert_eq!(cpu.flags.n, 1);
        cpu.step_word(pack_r(T0 as u32, T0 as u32, 1, 0, FUNCT_SRAV));
        assert_eq!(cpu.read(T0), 0xE000_0000);

        cpu.write(T1, 3);
        cpu.step_word(pack_r(T0 as u32, 1, T1 as u32, 0, FUNCT_SLLV));
        assert_eq!(cpu.read(T0), 8);
    }

    #[test]
    fn test_emu_rust_017() {
        let mut cpu = Cpu::new(DEFAULT_MEM);
        cpu.step_word(pack_i(OPCODE_ADDI, T0 as u32, 1, 0xFFFF));
        assert_eq!(cpu.read(T0), 0);
        assert_eq!(cpu.flags.z, 1);
        cpu.step_word(pack_i(OPCODE_ANDI, T0 as u32, 2, 0x00FF));
        assert_eq!(cpu.read(T0), 0xFF);
        cpu.step_word(pack_i(OPCODE_ORI, T0 as u32, 0, 1));
        assert_eq!(cpu.read(T0), 1);
        cpu.step_word(pack_i(OPCODE_XORI, T0 as u32, 2, 0));
        assert_eq!(cpu.read(T0), MASK);
    }

    #[test]
    fn test_emu_rust_018() {
        let mut cpu = Cpu::new(DEFAULT_MEM);
        let flags = cpu.flags;
        cpu.step_word(pack_i(OPCODE_LUI, T0 as u32, 0, 0x1234));
        assert_eq!(cpu.read(T0), 0x1234_0000);
        assert_eq!(cpu.flags, flags);
        cpu.step_word(pack_i(OPCODE_ORI, T0 as u32, T0 as u32, 0x5678));
        assert_eq!(cpu.read(T0), 0x1234_5678);

        let mut cpu = Cpu::new(DEFAULT_MEM);
        assert_eq!(cpu.pc, 0);
        cpu.step_word(pack_i(OPCODE_ADR, T0 as u32, 0, 16));
        assert_eq!(cpu.read(T0), 20);
    }

    #[test]
    fn test_emu_rust_019() {
        let mut cpu = Cpu::new(DEFAULT_MEM);
        cpu.step_word(pack_r(T0 as u32, 1, 2, 0, FUNCT_MUL));
        assert_eq!(cpu.read(T0), MASK);
        cpu.step_word(pack_r(T0 as u32, 2, 2, 0, FUNCT_MUL));
        assert_eq!(cpu.read(T0), 1);
        cpu.step_word(pack_r(T0 as u32, 2, 1, 0, FUNCT_DIV));
        assert_eq!(cpu.read(T0), MASK);
        cpu.step_word(pack_r(T0 as u32, 2, 0, 0, FUNCT_DIV));
        assert_eq!(cpu.read(T0), 0);
        assert_eq!(cpu.flags.z, 1);
    }

    #[test]
    fn test_emu_rust_012() {
        let mut cpu = Cpu::new(DEFAULT_MEM);
        cpu.step_word(add(T0 as u32, 1, 1));
        assert_eq!(cpu.pc, 4);
        cpu.pc = 1;
        cpu.step_word(add(T0 as u32, 1, 1));
        assert_eq!(cpu.cause, CAUSE_ALIGN);
        assert_eq!(cpu.pc, TRAP_VECTOR);
    }

    #[test]
    fn test_emu_rust_020() {
        let mut cpu = Cpu::new(DEFAULT_MEM);
        cpu.mem_store(0, &[0x78, 0x56, 0x34, 0x12]).unwrap();
        cpu.step_word(pack_i(OPCODE_LW, T0 as u32, 0, 0));
        assert_eq!(cpu.read(T0), 0x1234_5678);

        let mut cpu = Cpu::new(DEFAULT_MEM);
        cpu.write(T0, 0x1234_5678);
        cpu.step_word(pack_i(OPCODE_SW, T0 as u32, 0, 0));
        assert_eq!(&cpu.mem[0..4], &[0x78, 0x56, 0x34, 0x12]);

        let mut cpu = Cpu::new(DEFAULT_MEM);
        cpu.mem_store(0, &[0xFF]).unwrap();
        cpu.step_word(pack_i(OPCODE_LB, T0 as u32, 0, 0));
        assert_eq!(cpu.read(T0), MASK);
        cpu.step_word(pack_i(OPCODE_LBU, T0 as u32, 0, 0));
        assert_eq!(cpu.read(T0), 0xFF);

        let mut cpu = Cpu::new(DEFAULT_MEM);
        cpu.mem_store(3, &[0xAA, 0xBB, 0xCC]).unwrap();
        cpu.step_word(pack_i(OPCODE_SB, 1, 0, 4));
        assert_eq!(cpu.mem[4], 1);
        assert_eq!(cpu.mem[3], 0xAA);
        assert_eq!(cpu.mem[5], 0xCC);

        let mut cpu = Cpu::new(DEFAULT_MEM);
        cpu.mem_store(8, &[0xFF, 0x80]).unwrap();
        cpu.step_word(pack_i(OPCODE_LH, T0 as u32, 0, 8));
        assert_eq!(cpu.read(T0), 0xFFFF_80FF);
        cpu.step_word(pack_i(OPCODE_LHU, T0 as u32, 0, 8));
        assert_eq!(cpu.read(T0), 0x80FF);

        let mut cpu = Cpu::new(DEFAULT_MEM);
        cpu.write(T0, 0x80FF);
        cpu.step_word(pack_i(OPCODE_SH, T0 as u32, 0, 8));
        assert_eq!(&cpu.mem[8..10], &[0xFF, 0x80]);

        cpu.cause = 0;
        cpu.step_word(pack_i(OPCODE_LW, T0 as u32, 0, 1));
        assert_eq!(cpu.cause, CAUSE_ALIGN);
        assert_eq!(cpu.pc, TRAP_VECTOR);
    }

    #[test]
    fn test_emu_rust_021() {
        let mut cpu = Cpu::new(DEFAULT_MEM);
        cpu.step_word(pack_j(OPCODE_J, 0x20 >> 2));
        assert_eq!(cpu.pc, 0x20);

        let mut cpu = Cpu::new(DEFAULT_MEM);
        cpu.step_word(pack_j(OPCODE_JAL, 0x20 >> 2));
        assert_eq!(cpu.read(RA), 4);
        assert_eq!(cpu.pc, 0x20);
        cpu.step_word(pack_r(0, RA as u32, 0, 0, FUNCT_JR));
        assert_eq!(cpu.pc, 4);

        let mut cpu = Cpu::new(DEFAULT_MEM);
        cpu.write(T1, 0x40);
        cpu.step_word(pack_r(T0 as u32, T1 as u32, 0, 0, FUNCT_JALR));
        assert_eq!(cpu.read(T0), 4);
        assert_eq!(cpu.pc, 0x40);
    }

    #[test]
    fn test_emu_rust_022() {
        let mut cpu = Cpu::new(DEFAULT_MEM);
        cpu.step_word(pack_r(0, 1, 1, 0, FUNCT_CMP));
        cpu.step_word(bcc_to(cpu.pc, COND_EQ, 0x20));
        assert_eq!(cpu.pc, 0x20);

        let mut cpu = Cpu::new(DEFAULT_MEM);
        cpu.step_word(pack_r(0, 1, 0, 0, FUNCT_CMP));
        cpu.step_word(bcc_to(cpu.pc, COND_EQ, 0x20));
        assert_eq!(cpu.pc, 8);

        let mut cpu = Cpu::new(DEFAULT_MEM);
        cpu.step_word(pack_r(0, 1, 1, 0, FUNCT_TEST));
        cpu.step_word(bcc_to(cpu.pc, COND_NE, 0x20));
        assert_eq!(cpu.pc, 0x20);

        let mut cpu = Cpu::new(DEFAULT_MEM);
        cpu.step_word(pack_r(0, 0, 1, 0, FUNCT_CMP));
        cpu.step_word(bcc_to(cpu.pc, COND_LO, 0x20));
        assert_eq!(cpu.pc, 0x20);
    }
}
