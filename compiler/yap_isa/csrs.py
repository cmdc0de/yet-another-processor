"""COP0 CSR indices, STATUS bits, and CAUSE codes (design.md)."""

CSR_STATUS = 0
CSR_FLAGS = 1
CSR_EPC = 2
CSR_CAUSE = 3
CSR_UBASE = 4
CSR_ULIMIT = 5

CSR_BY_NAME = {
    "status": CSR_STATUS,
    "flags": CSR_FLAGS,
    "epc": CSR_EPC,
    "cause": CSR_CAUSE,
    "ubase": CSR_UBASE,
    "ulimit": CSR_ULIMIT,
}

STATUS_IE = 0
STATUS_P = 1
STATUS_TE = 2
STATUS_PIE = 8
STATUS_PP = 9

CAUSE_IRQ = 1
CAUSE_PROT = 2
CAUSE_SYS = 3
CAUSE_TLB_MISS = 4
CAUSE_PAGE_FAULT = 5
CAUSE_COP = 6
CAUSE_PRIV = 7
CAUSE_ALIGN = 8

TRAP_VECTOR = 0x80

COP0_MFC0 = 0
COP0_MTC0 = 4
COP1_MFC1 = 0
COP1_MTC1 = 4


def parse_csr(name: str) -> int:
    key = name.strip().lower()
    if key not in CSR_BY_NAME:
        raise ValueError(f"unknown csr: {name!r}")
    return CSR_BY_NAME[key]
