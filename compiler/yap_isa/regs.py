"""32 architectural GPR names. r0–r2 are wired; ABI names from design.md."""

GPR_COUNT = 32

# Index → canonical ABI name (rN always also accepted).
NUM_TO_NAME = {
    0: "zero",
    1: "one",
    2: "ones",
    3: "ra",
    4: "sp",
    5: "a0",
    6: "a1",
    7: "a2",
    8: "a3",
    9: "a4",
    10: "t0",
    11: "t1",
    12: "t2",
    13: "t3",
    14: "t4",
    15: "t5",
    16: "s0",
    17: "s1",
    18: "s2",
    19: "s3",
    20: "s4",
    21: "s5",
    22: "s6",
    23: "s7",
    24: "s8",
    25: "s9",
    26: "s10",
    27: "s11",
    28: "t6",
    29: "t7",
    30: "fp",
    31: "k0",
}

NAME_TO_NUM = {name: num for num, name in NUM_TO_NAME.items()}
for i in range(GPR_COUNT):
    NAME_TO_NUM[f"r{i}"] = i
# Syscall errno alias for r9 (design.md).
NAME_TO_NUM["err"] = 9


def parse_reg(name: str) -> int:
    key = name.strip().lower()
    if key not in NAME_TO_NUM:
        raise ValueError(f"unknown or out-of-range register: {name!r}")
    return NAME_TO_NUM[key]


def parse_freg(name: str) -> int:
    key = name.strip().lower()
    if key.startswith("f") and key[1:].isdigit():
        idx = int(key[1:])
        if 0 <= idx < 32:
            return idx
    raise ValueError(f"unknown fp register: {name!r}")
