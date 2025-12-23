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
# 2. IDENTIFICATION REGEX (FUNDS + SWEEP)
# ---------------------------------------------------------
# Recognises:
# - FUNDS TRANSFER TO ACCT xxxx
# - FUNDS TRANSFER FROM ACCOUNT xxxx
# - SWEEP TRANSFER FROM INVESTMENT ACCT xxxx
# - SWEEP TRANSFR TO ACCT xxxx
FUNDS_TRANSFER_FRMDEP_RECOGNISE_RE = re.compile(
    r"\b(?:FUNDS|SWEEP)\s+TRANSF(?:ER|R)\b.*\b(FROM|TO)\s+(?:INVESTMENT\s+)?(?:ACCT|ACCOUNT)\b"
)


def is_funds_transfer_frmdep(line: str) -> bool:
    norm = normalize_narrative(line)
    if not norm:
        return False
    return bool(FUNDS_TRANSFER_FRMDEP_RECOGNISE_RE.search(norm))


# ---------------------------------------------------------
# 3. PARSING REGEX (SUPPORTS ALL VARIANTS)
# ---------------------------------------------------------
FUNDS_TRANSFER_FRMDEP_PARSE_RE = re.compile(
    r"""
    (?:REF\s+(?P<REF_NO>\w+)\s+)?                 # optional REF
    (?:FUNDS|SWEEP)\s+TRANSF(?:ER|R)\s+
    (?:FRMDEP\s+)?                                # optional FRMDEP
    (?:
        FROM\s+(?:INVESTMENT\s+)?(?:ACCT|ACCOUNT)\s+(?P<FROM_ACCOUNT>\S+) |
        TO\s+(?:INVESTMENT\s+)?(?:ACCT|ACCOUNT)\s+(?P<TO_ACCOUNT>\S+)
    )
    (?:\s+FROM\s+(?P<FROM_ENTITY>.+))?            # optional entity
    $
    """,
    re.VERBOSE
)


# ---------------------------------------------------------
# 4. PARSER (FACTS ONLY — NO PAYER/PAYEE)
# ---------------------------------------------------------
def parse_funds_transfer_frmdep(line: str) -> dict:
    norm = normalize_narrative(line)

    match = FUNDS_TRANSFER_FRMDEP_PARSE_RE.search(norm)
    if not match:
        return {}

    from_acct = match.group("FROM_ACCOUNT")
    to_acct = match.group("TO_ACCOUNT")

    out = {
        "TRANS_TYPE": "Internal Funds Transfer"
    }

    if match.group("REF_NO"):
        out["REF_NO"] = match.group("REF_NO")

    # FROM ACCT → ORIG (account number allowed)
    if from_acct:
        out["FROM_ACCOUNT"] = from_acct
        out["ORIG"] = from_acct

    # TO ACCT → BNF (account number allowed)
    if to_acct:
        out["TO_ACCOUNT"] = to_acct
        out["BNF"] = to_acct

    if match.group("FROM_ENTITY"):
        out["ENTITY"] = match.group("FROM_ENTITY")

    return out
