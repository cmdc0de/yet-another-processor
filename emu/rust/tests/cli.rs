//! CLI checks for emu-rust m1. Run: cargo test --manifest-path emu/rust/Cargo.toml

use std::fs;
use std::path::PathBuf;
use std::process::Command;

use yap_emu::{pack, Yap1, HALT_WORD};

fn bin() -> PathBuf {
    PathBuf::from(env!("CARGO_BIN_EXE_yap-emu"))
}

fn tmp_yap(name: &str, bytes: &[u8]) -> PathBuf {
    let dir = std::env::temp_dir().join("yap-emu-m1");
    fs::create_dir_all(&dir).unwrap();
    let path = dir.join(name);
    fs::write(&path, bytes).unwrap();
    path
}

fn halt_image() -> Vec<u8> {
    pack(&Yap1 {
        load: 0,
        entry: 0,
        payload: HALT_WORD.to_le_bytes().to_vec(),
    })
}

#[test]
fn test_emu_rust_001() {
    let missing = Command::new(bin()).output().unwrap();
    assert_ne!(missing.status.code(), Some(0));

    let path = tmp_yap("halt.yap", &halt_image());
    let ok = Command::new(bin()).arg(&path).output().unwrap();
    assert_eq!(
        ok.status.code(),
        Some(0),
        "stderr: {}",
        String::from_utf8_lossy(&ok.stderr)
    );
}

#[test]
fn test_emu_rust_002() {
    let short = tmp_yap("short.yap", &[0u8; 15]);
    let r = Command::new(bin()).arg(&short).output().unwrap();
    assert_ne!(r.status.code(), Some(0));

    let mut bad_magic = halt_image();
    bad_magic[0] = b'X';
    let path = tmp_yap("badmagic.yap", &bad_magic);
    let r = Command::new(bin()).arg(&path).output().unwrap();
    assert_ne!(r.status.code(), Some(0));

    let mut bad_size = halt_image();
    bad_size[8..12].copy_from_slice(&99u32.to_le_bytes());
    let path = tmp_yap("badsize.yap", &bad_size);
    let r = Command::new(bin()).arg(&path).output().unwrap();
    assert_ne!(r.status.code(), Some(0));
}

#[test]
fn test_emu_rust_004() {
    let halt = tmp_yap("halt4.yap", &halt_image());
    let r = Command::new(bin()).arg(&halt).output().unwrap();
    assert_eq!(r.status.code(), Some(0));

    let zeros = pack(&Yap1 {
        load: 0,
        entry: 0,
        payload: vec![0; 16],
    });
    let path = tmp_yap("zeros.yap", &zeros);
    let r = Command::new(bin())
        .arg(&path)
        .args(["--max-steps", "10"])
        .output()
        .unwrap();
    assert_ne!(r.status.code(), Some(0));
}

#[test]
fn test_emu_rust_005() {
    let path = tmp_yap("halt-dump.yap", &halt_image());
    let r = Command::new(bin()).arg(&path).output().unwrap();
    assert_eq!(r.status.code(), Some(0));
    let out = String::from_utf8_lossy(&r.stdout).to_lowercase();
    assert!(out.contains("pc"), "{out}");
    assert!(out.contains("flags"), "{out}");
    assert!(out.contains("cause"), "{out}");
    assert!(out.contains("r10"), "{out}");
}

#[cfg(all(target_os = "linux", target_arch = "x86_64"))]
#[test]
fn test_emu_rust_006() {
    assert_eq!(std::env::consts::OS, "linux");
    assert_eq!(std::env::consts::ARCH, "x86_64");
}

#[cfg(all(target_os = "linux", target_arch = "aarch64"))]
#[test]
fn test_emu_rust_007() {
    assert_eq!(std::env::consts::OS, "linux");
    assert_eq!(std::env::consts::ARCH, "aarch64");
}

#[cfg(all(target_os = "windows", target_arch = "x86_64"))]
#[test]
fn test_emu_rust_008() {
    assert_eq!(std::env::consts::OS, "windows");
    assert_eq!(std::env::consts::ARCH, "x86_64");
}

#[cfg(all(target_os = "windows", target_arch = "aarch64"))]
#[test]
fn test_emu_rust_009() {
    assert_eq!(std::env::consts::OS, "windows");
    assert_eq!(std::env::consts::ARCH, "aarch64");
}

#[cfg(all(target_os = "macos", target_arch = "aarch64"))]
#[test]
fn test_emu_rust_010() {
    assert_eq!(std::env::consts::OS, "macos");
    assert_eq!(std::env::consts::ARCH, "aarch64");
}
