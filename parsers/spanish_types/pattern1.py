import re
import json


def normalize_narrative(line: str) -> str:
    if not line:
        return ""
    line = line.upper()
    line = re.sub(r"^[,|\\]+", "", line)
    line = re.sub(r"[\\|,]+$", "", line)
    line = re.sub(r"\s+", " ", line)
    return line.strip()


# ==========================
# 1️⃣ Pattern detection
# ==========================
# Rule:
#   Accept: /PT/DE/EI/...
#   Reject: anything without those flag prefixes
pattern1 = re.compile(
    r"^/?PT/DE/EI/",
    re.IGNORECASE
)


def is_pattern1(line: str) -> bool:
    if not line:
        return False
    line_n = normalize_narrative(line)
    return bool(pattern1.search(line_n))


# ==========================
# 2️⃣ Pattern parsing
# ==========================
# Full variant parser (ref + name + codes)
pattern1_full = re.compile(
    r"""
    ^
    /([A-Z/]+)                        # flags block
    \s+REF\.?\s+(\d+)                 # reference id
    \s+A\sF/V\s+(.+?)                 # beneficiary name
    \s+([A-Z0-9]{2,5})                # internal code
    \s+([0-9]{2})                     # sequence number
    (?:/([A-Z0-9]{2,10})/([0-9]{1,5})/([A-Z0-9]+))?   # optional trailing codes
    $
    """,
    re.IGNORECASE | re.VERBOSE
)


# Shortened variant parser (no REF / no name)
pattern1_short = re.compile(
    r"""
    ^
    /([A-Z/]+)          # flags block e.g. PT/DE/EI/
    ([0-9]+)?           # optional internal code at start (like 994)
    (?:[-\s]+(.+))?     # optional detail text (like INTERNET)
    $
    """,
    re.IGNORECASE | re.VERBOSE
)


def parse_pattern1(line: str) -> dict | None:
    if not line:
        return None

    txt = normalize_narrative(line)

    # Try full parser
    m = pattern1_full.match(txt)
    if m:
        (
            flags_raw,
            reference_id,
            beneficiary,
            internal_code,
            seq_no,
            tag,
            code,
            action_raw
        ) = m.groups()

        flags = [f for f in flags_raw.split("/") if f]

        result = {
            "flags": flags,
            "transaction_type": "PAYMENT",
            "beneficiary": beneficiary.strip(),
            "internal_code": internal_code.strip(),
            "reference_id": reference_id.strip(),
            "sequence_number": seq_no.strip(),
        }

        if tag:
            action = action_raw.replace(" ", "_").replace("-", "_")
            result.update({
                "control_tag": tag.strip(),
                "control_code": code.strip(),
                "transaction_action": action.strip()
            })

        return result

    # Try short parser
    m = pattern1_short.match(txt)
    if m:
        flags_raw, internal_code, detail = m.groups()
        flags = [f for f in flags_raw.split("/") if f]

        return {
            "flags": flags,
            "transaction_type": "PAYMENT",
            "internal_code": internal_code.strip() if internal_code else None,
            "detail": detail.strip() if detail else None
        }

    return None


# ==========================
# 3️⃣ Test harness
# ==========================
if __name__ == "__main__":
    print(json.dumps(parse_pattern1(input()), indent=1))
