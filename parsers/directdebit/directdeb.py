import re

def normalize_narrative(line: str) -> str:
    if not line:
        return ""
    line = re.sub(r"^[,|]+", "", line)
    line = re.sub(r"[\\|,]+$", "", line)
    line = re.sub(r"\s+", " ", line)
    return line.strip().upper()

DIRECT_DEBIT_RE = re.compile(
    r"""
    \b(
        DIRECT\s+DEB(IT)? |
        DIRECT\s+DEBIT |
        DEB\s+ |
        PYMT |
        PURCHASE |
        BENEFITS |
        INS\s+CO |
        INSURANCE
    )\b
    """,
    re.VERBOSE
)


DIRECT_DEBIT_EXCLUDE_RE = re.compile(
    r"""
    \b(
        ACH |
        WIRE |
        CARD |
        RDC |
        CHECK |
        PAYPAL |
        AVIDPAY |
        RMR |
        VENDORPYMT
    )\b
    """,
    re.VERBOSE
)

def is_direct_debit(line: str) -> bool:
    norm = normalize_narrative(line)
    if not norm:
        return False

    if DIRECT_DEBIT_EXCLUDE_RE.search(norm):
        return False

    return bool(DIRECT_DEBIT_RE.search(norm))

REF_RE = re.compile(r"\b[A-Z0-9\-]{6,}\b")

def parse_direct_debit(line: str) -> dict:
    norm = normalize_narrative(line)

    tokens = norm.split()

    # Heuristic: counterparty = leading alpha block before debit keywords
    counterparty_parts = []
    for t in tokens:
        if t in {"DIRECT", "DEBIT", "DEB", "PYMT", "PURCHASE"}:
            break
        counterparty_parts.append(t)

    counterparty = " ".join(counterparty_parts).strip() or None

    refs = REF_RE.findall(norm)

    return {
        "TRANS_TYPE": "DIRECT_DEBIT",
        "COUNTERPARTY_NAME": counterparty,
        "REFERENCE_IDS": refs,
        "RAW": norm
    }
