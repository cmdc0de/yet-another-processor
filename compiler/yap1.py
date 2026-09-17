"""YAP1 image: 16-byte LE header + payload. CPU does not execute the header."""

from __future__ import annotations

import struct
from dataclasses import dataclass

MAGIC = b"YAP1"
HEADER_SIZE = 16
_HEADER = struct.Struct("<4sIII")


class Yap1Error(ValueError):
    pass


@dataclass(frozen=True)
class Yap1:
    load: int
    entry: int
    payload: bytes

    @property
    def size(self) -> int:
        return len(self.payload)


def pack(image: Yap1) -> bytes:
    header = _HEADER.pack(MAGIC, image.load & 0xFFFFFFFF, image.size, image.entry & 0xFFFFFFFF)
    return header + image.payload


def unpack(data: bytes) -> Yap1:
    if len(data) < HEADER_SIZE:
        raise Yap1Error("file shorter than YAP1 header")
    magic, load, size, entry = _HEADER.unpack(data[:HEADER_SIZE])
    if magic != MAGIC:
        raise Yap1Error("bad YAP1 magic")
    payload = data[HEADER_SIZE:]
    if size != len(payload):
        raise Yap1Error("YAP1 size does not match payload")
    return Yap1(load=load, entry=entry, payload=payload)
