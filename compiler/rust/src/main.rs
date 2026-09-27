//! yap-compiler m1: empty `fn main() {}` → YAP1 (load=0, entry=0).
//! Layout: j _start @0, halt @0x80, _start @0x84 (li sp, jal main, halt), main = jr ra.

use std::env;
use std::fs;
use std::path::Path;
use std::process;

const OPCODE_J: u32 = 0b000010;
const OPCODE_JAL: u32 = 0b000011;
const OPCODE_LUI: u32 = 0b001111;
const OPCODE_ORI: u32 = 0b001101;
const FUNCT_JR: u32 = 0b001000;
const FUNCT_HALT: u32 = 0b101100;
const RA: u32 = 3;
const SP: u32 = 4;
const ADDR_START: u32 = 0x84;
const ADDR_MAIN: u32 = 0x94;

fn pack_r(rd: u32, rs: u32, rt: u32, shamt: u32, funct: u32) -> u32 {
    (rd << 21) | (rs << 16) | (rt << 11) | (shamt << 6) | funct
}

fn pack_i(opcode: u32, rd: u32, rs: u32, imm16: u32) -> u32 {
    (opcode << 26) | (rd << 21) | (rs << 16) | (imm16 & 0xffff)
}

fn pack_j(opcode: u32, addr: u32) -> u32 {
    (opcode << 26) | ((addr >> 2) & 0x03ff_ffff)
}

fn halt() -> u32 {
    pack_r(0, 0, 0, 0, FUNCT_HALT)
}

fn strip_comments(src: &str) -> String {
    src.lines()
        .map(|line| match line.find("//") {
            Some(i) => &line[..i],
            None => line,
        })
        .collect::<Vec<_>>()
        .join("\n")
}

fn parse_empty_main(src: &str, path: &str) -> Result<(), String> {
    let text = strip_comments(src);
    let compact: String = text.chars().filter(|c| !c.is_whitespace()).collect();
    if compact == "fnmain(){}" {
        Ok(())
    } else {
        Err(format!("{path}:1: expected empty fn main() {{ }}"))
    }
}

fn compile_empty_main() -> Vec<u8> {
    let mut payload = vec![0u8; ADDR_MAIN as usize + 4];
    let mut put = |addr: u32, word: u32| {
        let i = addr as usize;
        payload[i..i + 4].copy_from_slice(&word.to_le_bytes());
    };
    put(0, pack_j(OPCODE_J, ADDR_START));
    put(0x80, halt());
    put(0x84, pack_i(OPCODE_LUI, SP, 0, 0));
    put(0x88, pack_i(OPCODE_ORI, SP, SP, 0x8000));
    put(0x8c, pack_j(OPCODE_JAL, ADDR_MAIN));
    put(0x90, halt());
    put(ADDR_MAIN, pack_r(0, RA, 0, 0, FUNCT_JR));
    payload
}

fn pack_yap1(payload: &[u8]) -> Vec<u8> {
    let mut out = Vec::with_capacity(16 + payload.len());
    out.extend_from_slice(b"YAP1");
    out.extend_from_slice(&0u32.to_le_bytes()); // load
    out.extend_from_slice(&(payload.len() as u32).to_le_bytes());
    out.extend_from_slice(&0u32.to_le_bytes()); // entry
    out.extend_from_slice(payload);
    out
}

fn compile_file(input: &Path, output: &Path) -> Result<(), String> {
    let src = fs::read_to_string(input).map_err(|e| format!("{}:1: {e}", input.display()))?;
    parse_empty_main(&src, &input.display().to_string())?;
    let image = pack_yap1(&compile_empty_main());
    fs::write(output, image).map_err(|e| format!("{}:1: {e}", output.display()))?;
    Ok(())
}

fn usage() -> ! {
    eprintln!("usage: yap-compiler input.ys -o output.yap");
    process::exit(2);
}

fn main() {
    let args: Vec<String> = env::args().skip(1).collect();
    let mut input: Option<String> = None;
    let mut output: Option<String> = None;
    let mut i = 0;
    while i < args.len() {
        if args[i] == "-o" {
            i += 1;
            if i >= args.len() {
                usage();
            }
            output = Some(args[i].clone());
        } else if args[i].starts_with('-') {
            usage();
        } else if input.is_none() {
            input = Some(args[i].clone());
        } else {
            usage();
        }
        i += 1;
    }
    let (Some(input), Some(output)) = (input, output) else {
        usage();
    };
    if let Err(e) = compile_file(Path::new(&input), Path::new(&output)) {
        eprintln!("{e}");
        process::exit(1);
    }
}
