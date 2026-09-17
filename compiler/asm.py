"""Assemble a .s file to YAP1. v1: no labels, no .org. python3 -m compiler.asm in.s -o out.yap"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from compiler.yap1 import Yap1, pack
from compiler.yap_isa import assemble


class AsmError(Exception):
    def __init__(self, path, line_no, message):
        self.path = path
        self.line_no = line_no
        self.message = message
        super().__init__(f"{path}:{line_no}: {message}")


def strip_comment(line: str) -> str:
    cut = len(line)
    for ch in ";#":
        i = line.find(ch)
        if i >= 0:
            cut = min(cut, i)
    return line[:cut].strip()


def assemble_source(text: str, path: str = "<src>") -> bytes:
    payload = bytearray()
    lc = 0
    for line_no, raw in enumerate(text.splitlines(), start=1):
        stmt = strip_comment(raw)
        if not stmt:
            continue
        try:
            word = assemble(stmt, pc=lc)
        except ValueError as exc:
            raise AsmError(path, line_no, str(exc)) from exc
        payload.extend(word.to_bytes(4, "little"))
        lc += 4
    return pack(Yap1(load=0, entry=0, payload=bytes(payload)))


def assemble_file(path: Path) -> bytes:
    text = path.read_text(encoding="utf-8")
    return assemble_source(text, path=str(path))


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(prog="compiler.asm", description="Assemble YAP assembly to YAP1")
    parser.add_argument("input", help="UTF-8 .s source")
    parser.add_argument("-o", "--output", required=True, help="YAP1 output path")
    args = parser.parse_args(argv)
    src = Path(args.input)
    dest = Path(args.output)
    try:
        data = assemble_file(src)
    except AsmError as exc:
        print(str(exc), file=sys.stderr)
        return 1
    except OSError as exc:
        print(f"{src}:1: {exc}", file=sys.stderr)
        return 1
    dest.write_bytes(data)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
