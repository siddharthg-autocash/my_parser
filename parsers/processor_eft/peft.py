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
    \b
    (?P<proc>[A-Z]{2,6})EFT      # processor code (RPI, YDI, APF, etc.)
    \s+
    (?P<date>\d{6})              # YYMMDD
    \s+
    (?P<ref>[A-Z0-9]{6,})        # reference
    (?:\s+(?P=ref))?             # optional repeated ref
    \b
    """,
    re.VERBOSE
)

def is_processor_eft(line: str) -> bool:
    norm = normalize_narrative(line)
    if not norm:
        return False

    # hard guards — do NOT collide with rails
    if any(k in norm for k in ("ACH", "WIRE", "FED", "RDC", "CARD", "TRN*", "RMR*")):
        return False

    return bool(PROCESSOR_EFT_RECOGNISE_RE.search(norm))

def parse_processor_eft(line: str) -> dict:
    norm = normalize_narrative(line)

    m = PROCESSOR_EFT_RECOGNISE_RE.search(norm)
    if not m:
        return {
            "META": norm,
            "ERROR": "PROCESSOR_EFT_PARSE_FAILED"
        }

    return {
        "TRANS_TYPE": "PROCESSOR_EFT",
        "PROCESSOR_CODE": m.group("proc"),
        "DATE": m.group("date"),
        "REFERENCE": m.group("ref")
    }

if __name__=='__main__':
    print(parse_processor_eft(input()))