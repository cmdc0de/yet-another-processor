//! Minimal CPU: little-endian SRAM, PC, halt. No ALU in m1.

use crate::yap1::Yap1;

pub const DEFAULT_MEM: usize = 65536;
pub const DEFAULT_MAX_STEPS: u32 = 100_000;
pub const HALT_WORD: u32 = 0x0000_002C;
const OPCODE_SPECIAL: u32 = 0;
const FUNCT_HALT: u32 = 0b101100;

#[derive(Debug)]
pub struct Cpu {
    pub mem: Vec<u8>,
    pub pc: u32,
    pub halted: bool,
}

impl Cpu {
    pub fn new(mem_size: usize) -> Self {
        Self {
            mem: vec![0; mem_size],
            pc: 0,
            halted: false,
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

    pub fn step(&mut self) -> Result<(), String> {
        if self.halted {
            return Ok(());
        }
        let word = self.fetch_u32(self.pc)?;
        if Self::is_halt_word(word) {
            self.halted = true;
        }
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
}
