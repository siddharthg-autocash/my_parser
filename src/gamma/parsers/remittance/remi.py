import re


def normalize_narrative(line: str) -> str:
    if not line:
        return ""

    line = line.lstrip(",")
    line = re.sub(r"[,\s]+$", "", line)
    line = re.sub(r"\s+", " ", line)

    return line.strip().upper()


# -------------------------------
# Recognition
# -------------------------------
def is_remittance_advice(line: str) -> bool:
    norm = normalize_narrative(line)
    if not norm:
        return False

    return "TRN*" in norm and "RMR*" in norm


# -------------------------------
# Regexes
# -------------------------------
REMITTANCE_PARSE_RE = re.compile(
    r"""
    ^
    (?P<PREFIX>.*?)
    \s*
    TRN\*(?P<TRN_SEQ>\d+)\*(?P<TRN_REF>[^\\]+)
    \\
    (?P<RMR_SEGMENT>RMR\*.+)
    $
    """,
    re.VERBOSE,
)

RMR_REF_RE = re.compile(r"RMR\*[^*]*\*([^\\]+)")
ID_TOKEN_RE = re.compile(r"\b[A-Z0-9]{8,}\b")


# -------------------------------
# Parser
# -------------------------------
def parse_remittance_advice(line: str) -> dict:
    norm = normalize_narrative(line)

    m = REMITTANCE_PARSE_RE.search(norm)
    if not m:
        return {
            "FORMAT": "REMITTANCE_ADVICE",
            "META": norm,
            "ERROR": "REMITTANCE_PARSE_FAILED",
        }

    rmr_raw = m.group("RMR_SEGMENT")

    # authoritative counterparty comes from RMR*
    cp_match = RMR_REF_RE.search(rmr_raw)
    counterparty = cp_match.group(1).strip() if cp_match else None

    # opaque references (no semantic guessing)
    refs = list(set(ID_TOKEN_RE.findall(norm)))

    return {
        "FORMAT": "REMITTANCE_ADVICE",
        "TRANS_TYPE": "EDI_REMITTANCE_FRAGMENT",
        "COUNTERPARTY_NAME": counterparty,
        "TRN_SEQUENCE": m.group("TRN_SEQ"),
        "TRN_REFERENCE": m.group("TRN_REF"),
        "RMR_RAW": rmr_raw,
        "REMITTANCE_REFS": refs,
        "RAW_REF": norm,
    }
