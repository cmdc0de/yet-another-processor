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


def _split_args(rest: str) -> list:
    return rest.replace(",", " ").split()


def _eval_imm(token: str, equ: dict, path, line_no) -> int:
    if token in equ:
        return equ[token]
    try:
        return int(token, 0)
    except ValueError as exc:
        raise AsmError(path, line_no, f"bad immediate: {token}") from exc


def _subst_equ(stmt: str, equ: dict) -> str:
    names = sorted(equ, key=len, reverse=True)
    out = stmt
    for name in names:
        hexv = hex(equ[name] & 0xFFFFFFFF)
        rebuilt = []
        for tok in out.split():
            if tok == name:
                rebuilt.append(hexv)
            elif tok.startswith(name + "("):
                rebuilt.append(hexv + tok[len(name) :])
            else:
                rebuilt.append(tok)
        out = " ".join(rebuilt)
    return out


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


def _align_pad(lc: int, n: int, path, line_no) -> int:
    if n < 0 or n > 31:
        raise AsmError(path, line_no, ".align n out of range")
    align = 1 << n
    return (align - (lc % align)) % align


def _ensure(payload: bytearray, size: int) -> None:
    if len(payload) < size:
        payload.extend(b"\x00" * (size - len(payload)))


def _emit(payload: bytearray, lc: int, data: bytes) -> None:
    _ensure(payload, lc + len(data))
    payload[lc : lc + len(data)] = data


def assemble_ex(text: str, path: str = "<src>"):
    """Return (YAP1 bytes, symbol table). Two-pass: labels/.org/data then emit."""
    load = 0
    items = []
    symbols = {}
    equ = {}
    lc = load
    for line_no, raw in enumerate(text.splitlines(), start=1):
        stmt = strip_comment(raw)
        if not stmt:
            continue
        match = _LABEL.match(stmt)
        if match:
            name, rest = match.group(1), match.group(2).strip()
            if name in symbols or name in equ:
                raise AsmError(path, line_no, f"duplicate symbol: {name}")
            symbols[name] = lc
            stmt = rest
            if not stmt:
                continue
        op = stmt.split()[0].lower()
        if op == ".org":
            lc = _parse_org(stmt, path, line_no, lc)
            items.append(("org", lc, line_no))
            continue
        if op == ".equ":
            parts = _split_args(stmt)
            if len(parts) != 3:
                raise AsmError(path, line_no, ".equ name, imm")
            name = parts[1]
            if name in symbols or name in equ:
                raise AsmError(path, line_no, f"duplicate symbol: {name}")
            equ[name] = _eval_imm(parts[2], equ, path, line_no)
            continue
        if op == ".align":
            parts = stmt.split()
            if len(parts) != 2:
                raise AsmError(path, line_no, ".align n")
            try:
                n = int(parts[1], 0)
            except ValueError as exc:
                raise AsmError(path, line_no, f"bad .align: {parts[1]}") from exc
            pad = _align_pad(lc, n, path, line_no)
            items.append(("pad", pad, line_no))
            lc += pad
            continue
        if op in (".byte", ".half", ".word"):
            width = {".byte": 1, ".half": 2, ".word": 4}[op]
            args = _split_args(stmt)[1:]
            if not args:
                raise AsmError(path, line_no, f"{op} needs at least one value")
            if lc % width != 0:
                raise AsmError(path, line_no, f"{op} requires {width}-byte alignment")
            items.append(("data", (width, args), line_no))
            lc += width * len(args)
            continue
        items.append(("insn", stmt, line_no))
        lc += 4

    payload = bytearray()
    lc = load
    for kind, data, line_no in items:
        if kind == "org":
            if data < lc:
                raise AsmError(path, line_no, ".org cannot move the location counter backward")
            _ensure(payload, data)
            lc = data
            continue
        if kind == "pad":
            _ensure(payload, lc + data)
            lc += data
            continue
        if kind == "data":
            width, args = data
            if lc % width != 0:
                raise AsmError(path, line_no, "unaligned data")
            blob = bytearray()
            for tok in args:
                val = _eval_imm(tok, equ, path, line_no)
                blob.extend((val & ((1 << (8 * width)) - 1)).to_bytes(width, "little"))
            _emit(payload, lc, bytes(blob))
            lc += len(blob)
            continue
        stmt = _subst_equ(data, equ)
        stmt = _resolve_targets(stmt, symbols, path, line_no)
        try:
            word = assemble(stmt, pc=lc)
        except ValueError as exc:
            raise AsmError(path, line_no, str(exc)) from exc
        _emit(payload, lc, word.to_bytes(4, "little"))
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
