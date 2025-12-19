import re

def normalize_narrative(line: str) -> str:
    if not line:
        return ""
    line = line.lstrip(",")
    line = re.sub(r"[,\s]+$", "", line)
    line = re.sub(r"\s+", " ", line)
    return line.strip().upper()

REMITTANCE_RECOGNISE_RE = re.compile(r"^(?!.*\bACH\b)(?!.*\bWIRE\b)(?!.*\bFED\b)(?!.*\bCARD\b)(?!.*\bRDC\b).*?\bTRN\*\d+\*[^\\]+\s*\\\s*RMR\*")


def is_remittance_advice(line: str) -> bool:
    norm = normalize_narrative(line)
    if not norm:
        return False
    return bool(REMITTANCE_RECOGNISE_RE.search(norm))

REMITTANCE_PARSE_RE = re.compile(
    r"""
    ^
    (?P<COUNTERPARTY_NAME>.*?)\s+
    TRN\*(?P<TRN_SEQ>\d+)\*(?P<TRN_REF>[^\\]+)
    \\
    (?P<RMR_SEGMENT>RMR\*.+)
    $
    """,
    re.VERBOSE
)

RMR_REF_RE = re.compile(r"RMR\*[^*]*\*([^\\]+)")
ID_TOKEN_RE = re.compile(r"\b[A-Z0-9]{8,}\b")

def parse_remittance_advice(line: str) -> dict:
    norm = normalize_narrative(line)

    m = REMITTANCE_PARSE_RE.search(norm)
    if not m:
        return {
            "FORMAT": "REMITTANCE_ADVICE",
            "META": norm,
            "ERROR": "REMITTANCE_PARSE_FAILED"
        }

    rmr_raw = m.group("RMR_SEGMENT")

    # extract logical references without guessing meaning
    refs = list(set(ID_TOKEN_RE.findall(norm)))

    return {
        "FORMAT": "REMITTANCE_ADVICE",
        "TRANS_TYPE": "EDI_REMITTANCE_FRAGMENT",
        "COUNTERPARTY_NAME": m.group("COUNTERPARTY_NAME").strip(),
        "TRN_SEQUENCE": m.group("TRN_SEQ"),
        "TRN_REFERENCE": m.group("TRN_REF"),
        "RMR_RAW": rmr_raw,
        "REMITTANCE_REFS": refs,
        "RAW_REF": norm
    }
