//! YAP1 image: 16-byte little-endian header plus payload. CPU does not execute the header.

pub const MAGIC: [u8; 4] = *b"YAP1";
pub const HEADER_SIZE: usize = 16;

#[derive(Debug, Clone, PartialEq, Eq)]
pub struct Yap1 {
    pub load: u32,
    pub entry: u32,
    pub payload: Vec<u8>,
}

#[derive(Debug, Clone, PartialEq, Eq)]
pub struct Yap1Error(pub String);

impl std::fmt::Display for Yap1Error {
    fn fmt(&self, f: &mut std::fmt::Formatter<'_>) -> std::fmt::Result {
        self.0.fmt(f)
    }
}

impl std::error::Error for Yap1Error {}

fn u32_le(data: &[u8]) -> u32 {
    u32::from_le_bytes(data.try_into().expect("4 bytes"))
}

pub fn unpack(data: &[u8]) -> Result<Yap1, Yap1Error> {
    if data.len() < HEADER_SIZE {
        return Err(Yap1Error("file shorter than YAP1 header".into()));
    }
    if data[0..4] != MAGIC {
        return Err(Yap1Error("bad YAP1 magic".into()));
    }
    let load = u32_le(&data[4..8]);
    let size = u32_le(&data[8..12]);
    let entry = u32_le(&data[12..16]);
    let payload = data[HEADER_SIZE..].to_vec();
    if size as usize != payload.len() {
        return Err(Yap1Error("YAP1 size does not match payload".into()));
    }
    Ok(Yap1 {
        load,
        entry,
        payload,
    })
}

pub fn pack(image: &Yap1) -> Vec<u8> {
    let mut out = Vec::with_capacity(HEADER_SIZE + image.payload.len());
    out.extend_from_slice(&MAGIC);
    out.extend_from_slice(&image.load.to_le_bytes());
    out.extend_from_slice(&(image.payload.len() as u32).to_le_bytes());
    out.extend_from_slice(&image.entry.to_le_bytes());
    out.extend_from_slice(&image.payload);
    out
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn unpack_rejects_short_and_bad_magic_and_size() {
        assert!(unpack(&[0u8; 15]).is_err());
        let mut bad = pack(&Yap1 {
            load: 0,
            entry: 0,
            payload: vec![0, 0, 0, 0],
        });
        bad[0] = b'X';
        assert!(unpack(&bad).is_err());
        bad = pack(&Yap1 {
            load: 0,
            entry: 0,
            payload: vec![0, 0, 0, 0],
        });
        bad[8..12].copy_from_slice(&99u32.to_le_bytes());
        assert!(unpack(&bad).is_err());
    }
}
