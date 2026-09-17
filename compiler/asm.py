"""Assemble a .s file to YAP1. python3 -m compiler.asm in.s -o out.yap"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

from compiler.yap1 import Yap1, pack, unpack
from compiler.yap_isa import Cpu, assemble
from compiler.yap_isa.encode import BRANCH_MNEMONIC

_LABEL = re.compile(r"^([A-Za-z_][A-Za-z0-9_]*):\s*(.*)$")
_NAME = re.compile(r"^[A-Za-z_][A-Za-z0-9_]*$")
_TARGET_OPS = frozenset({"j", "jal"}) | frozenset(BRANCH_MNEMONIC)
DEFAULT_MAX_STEPS = 100000
DEFAULT_MEM = 65536
_MAX_LAYOUT = 64


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


def _fits_s16(value: int) -> bool:
    return -0x8000 <= value <= 0x7FFF


def _li_insns(rd: str, imm: int) -> list:
    if _fits_s16(imm):
        return [f"addi {rd}, zero, {imm}"]
    u = imm & 0xFFFFFFFF
    hi = (u >> 16) & 0xFFFF
    lo = u & 0xFFFF
    return [f"lui {rd}, {hi}", f"ori {rd}, {rd}, {lo}"]


def _lookup_label(name: str, symbols: dict, prev_symbols: dict):
    if name in symbols:
        return symbols[name]
    if name in prev_symbols:
        return prev_symbols[name]
    return None


def _insn_nbytes(stmt: str, lc: int, symbols: dict, prev_symbols: dict, equ: dict, path, line_no) -> int:
    parts = _split_args(stmt)
    op = parts[0].lower()
    if op == "move":
        if len(parts) != 3:
            raise AsmError(path, line_no, "move rd, rs")
        return 4
    if op == "li":
        if len(parts) != 3:
            raise AsmError(path, line_no, "li rd, imm")
        imm = _eval_imm(parts[2], equ, path, line_no)
        return 4 if _fits_s16(imm) else 8
    if op == "la":
        if len(parts) != 3 or not _NAME.match(parts[2]):
            raise AsmError(path, line_no, "la rd, label")
        addr = _lookup_label(parts[2], symbols, prev_symbols)
        if addr is None:
            return 8
        return 4 if _fits_s16(addr - (lc + 4)) else 8
    return 4


def _expand_insn(stmt: str, lc: int, symbols: dict, equ: dict, path, line_no) -> list:
    parts = _split_args(stmt)
    op = parts[0].lower()
    if op == "move":
        if len(parts) != 3:
            raise AsmError(path, line_no, "move rd, rs")
        return [f"add {parts[1]}, {parts[2]}, zero"]
    if op == "li":
        if len(parts) != 3:
            raise AsmError(path, line_no, "li rd, imm")
        return _li_insns(parts[1], _eval_imm(parts[2], equ, path, line_no))
    if op == "la":
        if len(parts) != 3 or not _NAME.match(parts[2]):
            raise AsmError(path, line_no, "la rd, label")
        name = parts[2]
        if name not in symbols:
            raise AsmError(path, line_no, f"undefined label: {name}")
        addr = symbols[name]
        rel = addr - (lc + 4)
        if _fits_s16(rel):
            return [f"adr {parts[1]}, {rel}"]
        return _li_insns(parts[1], addr)
    return [stmt]


def _parse_source(text: str, path: str) -> list:
    entries = []
    for line_no, raw in enumerate(text.splitlines(), start=1):
        stmt = strip_comment(raw)
        if not stmt:
            continue
        label = None
        match = _LABEL.match(stmt)
        if match:
            label, rest = match.group(1), match.group(2).strip()
            stmt = rest
        if not stmt:
            entries.append((line_no, label, None, None))
            continue
        op = stmt.split()[0].lower()
        if op == ".org":
            kind = "org"
        elif op == ".equ":
            kind = "equ"
        elif op == ".align":
            kind = "align"
        elif op in (".byte", ".half", ".word"):
            kind = "data"
        else:
            kind = "insn"
        entries.append((line_no, label, kind, stmt))
    return entries


def _layout(entries: list, path: str, load: int):
    prev_symbols = {}
    symbols = {}
    equ = {}
    items = []
    for _ in range(_MAX_LAYOUT):
        symbols = {}
        equ = {}
        items = []
        lc = load
        for line_no, label, kind, stmt in entries:
            if label is not None:
                if label in symbols or label in equ:
                    raise AsmError(path, line_no, f"duplicate symbol: {label}")
                symbols[label] = lc
            if kind is None:
                continue
            if kind == "equ":
                parts = _split_args(stmt)
                if len(parts) != 3:
                    raise AsmError(path, line_no, ".equ name, imm")
                name = parts[1]
                if name in symbols or name in equ:
                    raise AsmError(path, line_no, f"duplicate symbol: {name}")
                equ[name] = _eval_imm(parts[2], equ, path, line_no)
                continue
            if kind == "org":
                lc = _parse_org(stmt, path, line_no, lc)
                items.append(("org", lc, line_no))
                continue
            if kind == "align":
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
            if kind == "data":
                op = stmt.split()[0].lower()
                width = {".byte": 1, ".half": 2, ".word": 4}[op]
                args = _split_args(stmt)[1:]
                if not args:
                    raise AsmError(path, line_no, f"{op} needs at least one value")
                if lc % width != 0:
                    raise AsmError(path, line_no, f"{op} requires {width}-byte alignment")
                items.append(("data", (width, args), line_no))
                lc += width * len(args)
                continue
            nbytes = _insn_nbytes(stmt, lc, symbols, prev_symbols, equ, path, line_no)
            items.append(("insn", (stmt, nbytes), line_no))
            lc += nbytes
        if symbols == prev_symbols:
            return items, symbols, equ, load
        prev_symbols = dict(symbols)
    raise AsmError(path, 1, "could not stabilize instruction sizes")


def assemble_ex(text: str, path: str = "<src>"):
    """Return (YAP1 bytes, symbol table). Two-pass: labels/.org/data then emit."""
    load = 0
    entries = _parse_source(text, path)
    items, symbols, equ, load = _layout(entries, path, load)
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
        stmt, nbytes = data
        words = _expand_insn(stmt, lc, symbols, equ, path, line_no)
        if 4 * len(words) != nbytes:
            raise AsmError(path, line_no, "internal size mismatch")
        for piece in words:
            piece = _subst_equ(piece, equ)
            piece = _resolve_targets(piece, symbols, path, line_no)
            try:
                word = assemble(piece, pc=lc)
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


def run_yap1(data: bytes, max_steps: int = DEFAULT_MAX_STEPS) -> int:
    image = unpack(data)
    need = max(image.load + image.size, image.entry + 4, DEFAULT_MEM)
    cpu = Cpu(mem_size=need)
    if image.size:
        cpu.mem_store(image.load, image.payload)
    cpu.pc = image.entry & 0xFFFFFFFF
    for _ in range(max(0, max_steps)):
        if cpu.halted:
            return 0
        if cpu.pc < 0 or cpu.pc + 4 > len(cpu.mem):
            return 1
        word = int.from_bytes(cpu.mem_load(cpu.pc, 4), "little")
        cpu.step(word)
    return 0 if cpu.halted else 1


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(prog="compiler.asm", description="Assemble YAP assembly to YAP1")
    parser.add_argument("input", help="UTF-8 .s source")
    parser.add_argument("-o", "--output", required=True, help="YAP1 output path")
    parser.add_argument("--run", action="store_true", help="load YAP1 into Cpu and step until halt")
    parser.add_argument(
        "--max-steps",
        type=int,
        default=DEFAULT_MAX_STEPS,
        help=f"step cap for --run (default {DEFAULT_MAX_STEPS})",
    )
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
    if args.run:
        return run_yap1(data, max_steps=args.max_steps)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
