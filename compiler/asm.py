"""Assemble a .s file to YAP1. python3 -m compiler.asm in.s -o out.yap"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

from compiler.yap1 import Yap1, pack
from compiler.yap_isa import assemble
from compiler.yap_isa.encode import BRANCH_MNEMONIC

_LABEL = re.compile(r"^([A-Za-z_][A-Za-z0-9_]*):\s*(.*)$")
_TARGET_OPS = frozenset({"j", "jal"}) | frozenset(BRANCH_MNEMONIC)


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


def _is_number(token: str) -> bool:
    try:
        int(token, 0)
        return True
    except ValueError:
        return False


def _parse_org(stmt: str, path, line_no, lc: int) -> int:
    parts = stmt.split()
    if len(parts) != 2:
        raise AsmError(path, line_no, ".org takes one immediate")
    try:
        imm = int(parts[1], 0)
    except ValueError as exc:
        raise AsmError(path, line_no, f"bad .org immediate: {parts[1]}") from exc
    if imm < 0:
        raise AsmError(path, line_no, ".org below load address")
    if imm < lc:
        raise AsmError(path, line_no, ".org cannot move the location counter backward")
    return imm


def _resolve_targets(stmt: str, symbols: dict, path, line_no) -> str:
    parts = stmt.replace(",", " ").split()
    if not parts:
        return stmt
    op = parts[0].lower()
    if op not in _TARGET_OPS or len(parts) != 2 or _is_number(parts[1]):
        return stmt
    name = parts[1]
    if name not in symbols:
        raise AsmError(path, line_no, f"undefined label: {name}")
    parts[1] = hex(symbols[name])
    return " ".join(parts)


def assemble_ex(text: str, path: str = "<src>"):
    """Return (YAP1 bytes, symbol table). Two-pass: labels/.org then emit."""
    load = 0
    items = []
    symbols = {}
    lc = load
    for line_no, raw in enumerate(text.splitlines(), start=1):
        stmt = strip_comment(raw)
        if not stmt:
            continue
        match = _LABEL.match(stmt)
        if match:
            name, rest = match.group(1), match.group(2).strip()
            if name in symbols:
                raise AsmError(path, line_no, f"duplicate label: {name}")
            symbols[name] = lc
            stmt = rest
            if not stmt:
                continue
        if stmt.split()[0].lower() == ".org":
            lc = _parse_org(stmt, path, line_no, lc)
            items.append(("org", lc, line_no))
            continue
        items.append(("insn", stmt, line_no))
        lc += 4

    payload = bytearray()
    lc = load
    for kind, data, line_no in items:
        if kind == "org":
            if data < lc:
                raise AsmError(path, line_no, ".org cannot move the location counter backward")
            if len(payload) < data:
                payload.extend(b"\x00" * (data - len(payload)))
            lc = data
            continue
        stmt = _resolve_targets(data, symbols, path, line_no)
        try:
            word = assemble(stmt, pc=lc)
        except ValueError as exc:
            raise AsmError(path, line_no, str(exc)) from exc
        if len(payload) < lc + 4:
            payload.extend(b"\x00" * (lc + 4 - len(payload)))
        payload[lc : lc + 4] = word.to_bytes(4, "little")
        lc += 4
    return pack(Yap1(load=load, entry=0, payload=bytes(payload))), symbols


def assemble_source(text: str, path: str = "<src>") -> bytes:
    data, _ = assemble_ex(text, path=path)
    return data


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
