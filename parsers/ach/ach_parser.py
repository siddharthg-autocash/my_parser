import json
try:
    from parsers.ach.keys import KEYS, INLINE_KEYS
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
    if k in ("REMAR K","R EMARK", "REMA RK", "REMARK"):
        return "REMARK"
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


def ach_parser_v2(v1_output: dict):
    out = {}

    for k, v in v1_output.items():
        if isinstance(v, str):
            out[k] = split_inline_keys(v)
        else:
            out[k] = v

    return out

# V1 — ACH PARSER

def ach_parser_v1(narr: str):
    marks = find_keys(narr, KEYS)

    idx = [0] + list(marks.keys()) + [len(narr)]
    out = {}
    
    # print(marks)

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

def ach_parser(narr: str):
    v1 = ach_parser_v1(narr)
    v2 = ach_parser_v2(v1)
    return v2

if __name__ == "__main__":
    # eg1.
    print(json.dumps(
        ach_parser("ORIG CO NAME=36 TREAS 310,ORIG ID=9101036151,DESC DATE=051425,ENTRY DESCR=MI SC PAY,ENTRY CLASS=CTX,TRACE NO=101036159719236,ENTRY DATE=250514,IND ID NO= 596012065360012,IND NAME=0017NORTH BROWARD HO,ORIG BANK=10103615"),
        indent=2
    ))

    # eg2.
    # print(json.dumps(
    #     ach_parser(
    #         "ACH Settlement TRANS TYPE=PPD SENDING CO. NAME=REALMANAGE LLC COMPANY ID=GENERATED "
    #         "DESCRIPTION=ACH OFFSET EFFECTIVE DATE=250502 RECV.ID NO=-SETT-ISOACHORG "
    #         "RECV. NAME=REALMANAG DISCRETIONARY DATA=04 TRACE NUMBER=025122004008569"
    #     ),
    #     indent=2
    # ))
    pass
