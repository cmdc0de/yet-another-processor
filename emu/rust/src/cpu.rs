//! CPU: little-endian SRAM, PC, halt, GPRs, FLAGS, SPECIAL ALU (m1–m2).

use crate::yap1::Yap1;

pub const DEFAULT_MEM: usize = 65536;
pub const DEFAULT_MAX_STEPS: u32 = 100_000;
pub const HALT_WORD: u32 = 0x0000_002C;
pub const MASK: u32 = 0xFFFF_FFFF;
pub const T0: usize = 10;

const OPCODE_SPECIAL: u32 = 0;
const FUNCT_SLL: u32 = 0b000000;
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
}

impl Cpu {
    pub fn new(mem_size: usize) -> Self {
        Self {
            mem: vec![0; mem_size],
            pc: 0,
            halted: false,
            gprs: [0; 32],
            flags: Flags::default(),
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

    fn execute(&mut self, word: u32) {
        let opcode = (word >> 26) & 0x3F;
        if opcode != OPCODE_SPECIAL {
            return;
        }
        let rd = ((word >> 21) & 0x1F) as usize;
        let rs_i = ((word >> 16) & 0x1F) as usize;
        let rt_i = ((word >> 11) & 0x1F) as usize;
        let shamt = (word >> 6) & 0x1F;
        let funct = word & 0x3F;
        let rs = self.read(rs_i);
        let rt = self.read(rt_i);
        let (result, write) = match funct {
            FUNCT_ADD => (self.alu_add(rs, rt), true),
            FUNCT_SUB => (self.alu_sub(rs, rt), true),
            FUNCT_AND => (self.alu_logic(rs & rt), true),
            FUNCT_OR => (self.alu_logic(rs | rt), true),
            FUNCT_XOR => (self.alu_logic(rs ^ rt), true),
            FUNCT_NOT => (self.alu_logic(!rs), true),
            FUNCT_SLL => (self.alu_sll(rs, shamt), true),
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
    }

    pub fn step_word(&mut self, word: u32) {
        if self.halted {
            return;
        }
        self.execute(word);
        self.pc = self.pc.wrapping_add(4);
    }

    pub fn step(&mut self) -> Result<(), String> {
        if self.halted {
            return Ok(());
        }
        let word = self.fetch_u32(self.pc)?;
        self.execute(word);
        self.pc = self.pc.wrapping_add(4);
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
}
