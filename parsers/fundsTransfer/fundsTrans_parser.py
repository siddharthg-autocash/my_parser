import re

# ---------------------------------------------------------
# 1. NORMALIZATION (shared across all parsers)
# ---------------------------------------------------------
def normalize_narrative(line: str) -> str:
    if not line:
        return ""
    line = line.lstrip(",")
    line = re.sub(r"\s+", " ", line)
    return line.strip().upper()


# ---------------------------------------------------------
# 2. IDENTIFICATION REGEX
# ---------------------------------------------------------
FUNDS_TRANSFER_FRMDEP_RECOGNISE_RE = re.compile(
    r"^REF\s+\w+\s+FUNDS\s+TRANSFER\s+FRMDEP\s+\S+\s+FROM\s+.+$"
)


def is_funds_transfer_frmdep(line: str) -> bool:
    norm = normalize_narrative(line)
    if not norm:
        return False
    return bool(FUNDS_TRANSFER_FRMDEP_RECOGNISE_RE.search(norm))


# ---------------------------------------------------------
# 3. PARSING REGEX
# ---------------------------------------------------------
FUNDS_TRANSFER_FRMDEP_PARSE_RE = re.compile(
    r"""
    ^REF\s+(?P<REF_NO>\w+)\s+
    FUNDS\s+TRANSFER\s+FRMDEP\s+
    (?P<FROM_ACCOUNT>\S+)\s+
    FROM\s+(?P<FROM_ENTITY>.+)
    $
    """,
    re.VERBOSE
)


def parse_funds_transfer_frmdep(line: str) -> dict:
    norm = normalize_narrative(line)

    match = FUNDS_TRANSFER_FRMDEP_PARSE_RE.search(norm)
    if not match:
        return {}

    return {
        "REF_NO": match.group("REF_NO"),
        "TRANS_TYPE": "FUNDS_TRANSFER_FRMDEP",
        "FROM_ACCOUNT": match.group("FROM_ACCOUNT"),
        "ENTITY": match.group("FROM_ENTITY"),
    }
