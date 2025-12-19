import re

# ---------------------------------------------------------
# 1. Normalization (run ONCE before any recognition/parsing)
# ---------------------------------------------------------
def normalize_narrative(line: str) -> str:
    if not line:
        return ""
    line = line.lstrip(",")
    line = re.sub(r"\s+", " ", line)
    return line.strip().upper()

PROCESSOR_EFT_RECOGNISE_RE = re.compile(
    r"""
    ^
    (?P<proc>[A-Z][A-Z0-9 .,&'-]{0,60}?)            # processor name
    \s+
    (?P<code>[A-Z]{1,6})                            # code letters
    (?P<id>\d{3,9})?                                # optional numeric id
    (?P<date>\d{6})?                                # optional merged date
    (?:\s+(?P<date2>\d{6}))?                        # optional spaced date
    \s*
    (?P<refs>.*)                                    # refs can begin immediately
    $
    """,
    re.VERBOSE
)



def is_processor_eft(line: str) -> bool:
    norm = normalize_narrative(line)
    if not norm:
        return False

    # hard guards — do NOT collide with rails
    if (
    "ACH" in norm
    or "WIRE" in norm
    or "FED" in norm
    or "RDC" in norm
    or re.search(r"\bCARD\b", norm)): return False


    return bool(PROCESSOR_EFT_RECOGNISE_RE.search(norm))

def parse_processor_eft(line: str) -> dict:
    norm = normalize_narrative(line)

    m = PROCESSOR_EFT_RECOGNISE_RE.search(norm)
    if not m:
        return {
            "META": norm,
            "ERROR": "PROCESSOR_EFT_PARSE_FAILED"
        }

    # Split references by comma or space, remove empty entries
    ref_block = m.group("refs")
    refs = re.split(r"[\s,]+", ref_block)
    refs = [r for r in refs if r]

    return {
        "TRANS_TYPE": "PROCESSOR_EFT",
        "PROCESSOR_NAME": m.group("proc").strip(),
        "PROCESSOR_CODE": m.group("code"),
        "DATE": m.group("date"),
        "REFERENCE_IDS": refs,
        "RAW": norm
    }

import json
if __name__=='__main__':
    print(json.dumps(parse_processor_eft(input()),indent=4))