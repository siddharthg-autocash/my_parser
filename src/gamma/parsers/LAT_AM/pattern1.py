import re
import json
from typing import Dict, Optional


# -------------------------------------------------
# 0. NORMALIZATION
# -------------------------------------------------

def normalize_narrative(line: str) -> str:
    if not line:
        return ""
    line = line.upper()
    line = re.sub(r"^[,|\\]+", "", line)
    line = re.sub(r"[\\|,]+$", "", line)
    line = re.sub(r"\s+", " ", line)
    return line.strip()


# -------------------------------------------------
# 1. PATTERN-1 UMBRELLA
# -------------------------------------------------

def is_pattern1(line: str) -> bool:
    return normalize_narrative(line).startswith("/PT/")


# -------------------------------------------------
# 2. VARIANT DETECTION (GENERAL)
# -------------------------------------------------

def is_pattern1a(line: str) -> bool:
    """
    Pattern-1A:
    Fixed positional grammar.
    Extremely strict by design.
    """
    txt = normalize_narrative(line)
    return bool(re.match(r"^/PT/DE/EI/", txt))


def is_pattern1b(line: str) -> bool:
    """
    Pattern-1B:
    Slash key-value grammar.
    Keys are short (1–4 chars), values arbitrary.
    """
    txt = normalize_narrative(line)

    if not txt.startswith("/PT/"):
        return False

    parts = [p for p in txt.split("/") if p]
    if len(parts) < 4:
        return False

    kv_pairs = 0
    i = 1
    while i + 1 < len(parts):
        key = parts[i]
        val = parts[i + 1]

        if 1 <= len(key) <= 4 and val:
            kv_pairs += 1
            i += 2
        else:
            i += 1

    # Require at least two KV pairs → settlement-style grammar
    return kv_pairs >= 2


def is_pattern1c(line: str) -> bool:
    """
    Pattern-1C:
    Hybrid / degraded / partially structured slash grammar.
    Examples:
    - missing values
    - extra noise
    - irregular KV grouping
    """
    txt = normalize_narrative(line)

    if not txt.startswith("/PT/"):
        return False

    # Has slashes but does NOT satisfy clean KV grammar
    parts = [p for p in txt.split("/") if p]
    return len(parts) >= 3


def detect_pattern1_variant(line: str) -> str:
    """
    Deterministic variant detection.
    Order matters.
    """
    if is_pattern1a(line):
        return "1A"
    if is_pattern1b(line):
        return "1B"
    if is_pattern1c(line):
        return "1C"
    return "UNKNOWN"


# -------------------------------------------------
# 3. PATTERN-1A PARSER (POSITIONAL)
# -------------------------------------------------

pattern1a_full = re.compile(
    r"""
    ^
    /([A-Z/]+)
    \s+REF\.?\s+(\d+)
    \s+A\sF/V\s+(.+?)
    \s+([A-Z0-9]{2,5})
    \s+([0-9]{2})
    (?:/([A-Z0-9]{2,10})/([0-9]{1,5})/([A-Z0-9]+))?
    $
    """,
    re.IGNORECASE | re.VERBOSE
)

pattern1a_short = re.compile(
    r"""
    ^
    /([A-Z/]+)
    ([0-9]+)?
    (?:[-\s]+(.+))?
    $
    """,
    re.IGNORECASE | re.VERBOSE
)


def parse_pattern1a(line: str) -> Optional[Dict]:
    txt = normalize_narrative(line)

    m = pattern1a_full.match(txt)
    if m:
        (
            flags_raw,
            reference_id,
            beneficiary,
            internal_code,
            seq_no,
            tag,
            code,
            action
        ) = m.groups()

        return {
            "variant": "1A",
            "transaction_type": "PAYMENT",
            "flags": [f for f in flags_raw.split("/") if f],
            "reference_id": reference_id,
            "beneficiary": beneficiary.strip(),
            "internal_code": internal_code,
            "sequence_number": seq_no,
            "control_tag": tag,
            "control_code": code,
            "transaction_action": action,
        }

    m = pattern1a_short.match(txt)
    if m:
        flags_raw, internal_code, detail = m.groups()
        return {
            "transaction_type": "PAYMENT",
            "flags": [f for f in flags_raw.split("/") if f],
            "internal_code": internal_code,
            "detail": detail,
        }

    return None


# -------------------------------------------------
# 4. PATTERN-1B PARSER (STRICT SLASH-KV)
# -------------------------------------------------

from typing import Dict

def parse_pattern1b(line: str) -> Dict:
    txt = normalize_narrative(line)
    parts = [p for p in txt.split("/") if p]

    if not parts:
        return {}

    fields = {}

    i = 1
    while i + 1 < len(parts):
        key = parts[i]
        val = parts[i + 1]

        if 1 <= len(key) <= 4:
            if key not in fields:
                fields[key] = val.strip()
            i += 2
        else:
            i += 1

    result = {
        "transaction_type": "SETTLEMENT",
        "flags": parts[0].split(),
        **fields
    }

    return result



# -------------------------------------------------
# 5. PATTERN-1C PARSER (LENIENT / LOSSLESS)
# -------------------------------------------------

def parse_pattern1c(line: str) -> Dict:
    txt = normalize_narrative(line)
    parts = [p for p in txt.split("/") if p]

    return {
        "transaction_type": "PATTERN1_PARTIAL",
        "tokens": parts
    }


# -------------------------------------------------
# 6. UNIFIED ENTRY POINT
# -------------------------------------------------

def parse_pattern1(line: str) -> Optional[Dict]:
    if not is_pattern1(line):
        return None

    variant = detect_pattern1_variant(line)

    if variant == "1A":
        return parse_pattern1a(line)

    if variant == "1B":
        return parse_pattern1b(line)

    if variant == "1C":
        return parse_pattern1c(line)

    return {
        "raw": normalize_narrative(line)
    }

if __name__ == "__main__":
    pass
