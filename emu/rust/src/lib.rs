//! YAP host emulator. m1: load YAP1, little-endian SRAM, halt or step cap.

pub mod cpu;
pub mod yap1;

use std::path::Path;

pub use cpu::{Cpu, DEFAULT_MAX_STEPS, DEFAULT_MEM, HALT_WORD};
pub use yap1::{pack, unpack, Yap1, Yap1Error};

pub fn cli(args: impl IntoIterator<Item = String>) -> i32 {
    let args: Vec<String> = args.into_iter().collect();
    let mut path: Option<String> = None;
    let mut max_steps = DEFAULT_MAX_STEPS;
    let mut i = 0;
    while i < args.len() {
        match args[i].as_str() {
            "--max-steps" => {
                i += 1;
                let Some(text) = args.get(i) else {
                    eprintln!("yap-emu: --max-steps needs a value");
                    return 1;
                };
                match text.parse::<u32>() {
                    Ok(n) => max_steps = n,
                    Err(_) => {
                        eprintln!("yap-emu: bad --max-steps");
                        return 1;
                    }
                }
            }
            flag if flag.starts_with('-') => {
                eprintln!("yap-emu: unknown option {flag}");
                return 1;
            }
            other => {
                if path.is_some() {
                    eprintln!("yap-emu: extra argument {other}");
                    return 1;
                }
                path = Some(other.to_string());
            }
        }
        i += 1;
    }
    let Some(path) = path else {
        eprintln!("yap-emu: YAP1 image path required");
        return 1;
    };
    run_file(Path::new(&path), max_steps)
}

pub fn run_file(path: &Path, max_steps: u32) -> i32 {
    let data = match std::fs::read(path) {
        Ok(d) => d,
        Err(e) => {
            eprintln!("yap-emu: {e}");
            return 1;
        }
    };
    let image = match unpack(&data) {
        Ok(img) => img,
        Err(e) => {
            eprintln!("yap-emu: {e}");
            return 1;
        }
    };
    let mut cpu = match Cpu::from_image(&image) {
        Ok(cpu) => cpu,
        Err(e) => {
            eprintln!("yap-emu: {e}");
            return 1;
        }
    };
    let halted = cpu.run(max_steps);
    print!("{}", cpu.dump());
    if halted {
        0
    } else {
        1
    }
}
