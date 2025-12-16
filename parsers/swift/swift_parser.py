import json
try:
    from parsers.swift.keys import KEYS, INLINE_KEYS
except ModuleNotFoundError:
    from keys import KEYS, INLINE_KEYS

# CONFIG

KEYS = sorted(set(KEYS), key=len, reverse=True)
INLINE_KEYS = sorted(INLINE_KEYS, key=len, reverse=True)

ALLOWED = {' ', ':', '=',',', '/', '\\', '_', '#','-'}


# COMMON HELPERS

def is_standalone(text, i, k_len):
    before = text[i - 1] if i > 0 else ' '
    after  = text[i + k_len] if i + k_len < len(text) else ' '
    return before in ALLOWED and after in ALLOWED


def normalize_key(k: str):
    # if k in ("REMAR K","R EMARK", "REMA RK", "REMARK"):
    #     return "REMARK"
    return k


def find_keys(text, key_list):
    found = {}
    reserved = []

    for k in key_list:
        k_len = len(k)
        for i in range(len(text) - k_len + 1):
            if text[i:i + k_len] != k:
                continue
            if not is_standalone(text, i, k_len):
                continue
            if any(s <= i < e for s, e in reserved):
                continue

            found[i] = k
            reserved.append((i, i + k_len))

    return dict(sorted(found.items()))

# V2 — INLINE KEY SPLITTER

def split_inline_keys(text: str):
    marks = find_keys(text, INLINE_KEYS)

    if not marks:
        return text.strip()

    idx = [0] + list(marks.keys()) + [len(text)]
    out = {}

    out["value"] = text[:idx[1]].strip()

    for i in range(1, len(idx) - 1):
        start, end = idx[i], idx[i + 1]
        raw_k = marks[start]
        k = normalize_key(raw_k)

        z = start + len(raw_k)
        while z < len(text) and not text[z].isalnum():
            z += 1

        out[k] = text[z:end].strip()

    return out


def swift_parser_v2(v1_output: dict):
    out = {}

    for k, v in v1_output.items():
        if isinstance(v, str):
            out[k] = split_inline_keys(v)
        else:
            out[k] = v

    return out

# V1 — swift PARSER

def swift_parser_v1(narr: str):
    marks = find_keys(narr, KEYS)

    idx = [0] + list(marks.keys()) + [len(narr)]
    out = {}

    out["Meta"] = narr[:idx[1]].strip()

    for i in range(1, len(idx) - 1):
        start, end = idx[i], idx[i + 1]
        raw_k = marks[start]
        k = normalize_key(raw_k)

        z = start + len(raw_k)
        while z < len(narr) and not narr[z].isalnum():
            z += 1

        out[k] = narr[z:end].strip()

    return out

# PIPELINE

def swift_parser(narr: str):
    v1 = swift_parser_v1(narr)
    v2 = swift_parser_v2(v1)
    return v2

if __name__ == "__main__":
    # eg1.
    print(json.dumps(
        swift_parser("WIRE TRANSFER OUT        B          00  ORIGINATOR:INNOVAIRRE HOLDING CO LLC AC/8612045257 BENEFICIARY:BHAVYA KUMAR AC/910010016446103 M-1-303, SUN REAL HOMES, NEW RANIP AHMEDABAD BENEBNK:AXIS BANK LIMITED ABA:AXISINBB087 RFB: 202506800461 RECVBNK:BK AMER NYC ABA:026009593 BBI:/GOUR/ IBK:BANK OF AMERICA, N.A., NY ABA:026009593 TRN:256RG50222CN PARTIALREF:10109 DATE:250627 TIME:1250,FULL REFERENCE#:0627MMQFMPNB010109 UETR:6F2DE5AF-53A2-479B-B5C9-F08866B2A125"),
        indent=2
    ))
    pass
