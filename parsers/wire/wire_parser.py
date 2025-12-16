import json
try:
    from parsers.wire.keys import KEYS, INLINE_KEYS
except ModuleNotFoundError:
    from keys import KEYS, INLINE_KEYS


# CONFIG

KEYS = sorted(set(KEYS), key=len, reverse=True)
INLINE_KEYS = sorted(INLINE_KEYS, key=len, reverse=True)
ALLOWED = {' ', ':', '=', '/', '\\', '-', '_',',','-'}

# COMMON HELPERS

def is_standalone(text, i, k_len):
    before = text[i - 1] if i > 0 else ' '
    after  = text[i + k_len] if i + k_len < len(text) else ' '
    return before in ALLOWED and after in ALLOWED


def normalize_inline_key(k: str):
    # if k in ("/AC", "AC/"):
    #     return "AC"
    return k


def find_keys(text, key_list):
    """
    Find non-overlapping key positions.
    """
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

    # DEBUG (enable when needed)
    # print("KEY POSITIONS:", found)

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
        k = normalize_inline_key(raw_k)

        z = start + len(raw_k)
        while z < len(text) and not text[z].isalnum():
            z += 1

        out[k] = text[z:end].strip()

    return out


def wire_parser_v2(v1_output: dict):
    """
    Apply inline key splitting on all V1 values.
    """
    out = {}

    for k, v in v1_output.items():
        if 'WIRE' in k or 'SRC' in k:

            out[k] = v
        elif isinstance(v, str):
            out[k] = split_inline_keys(v)
        else:
            out[k] = v

    return out


# V1 — WIRE PARSER

def wire_parser_v1(narr: str):
    marks = find_keys(narr, KEYS)

    idx = [0] + list(marks.keys()) + [len(narr)]
    out = {}

    out["Meta"] = narr[:idx[1]].strip()

    for i in range(1, len(idx) - 1):
        start, end = idx[i], idx[i + 1]
        k = marks[start]
        z = start + len(k)

        while z < len(narr) and not narr[z].isalnum():
            z += 1

        out[k] = narr[z:end].strip()

    return out


# PIPELINE

def wire_parser(narr: str):
    v1 = wire_parser_v1(narr)
    v2 = wire_parser_v2(v1)
    return v2


if __name__ == "__main__":
    result = wire_parser("""Individual International Money Transfer Debit ORIG BANK ABA=071000288 ORIG BANK=BMO Bank N.A.     TYP=C REC BANK ABA=026005092 REC BANK=Wells Fargo Bank N FED REF=004484 SENT AT=2025/11/26 09:00 WIRE TYPE=FIO CURRENCY DESC=US DOLLAR EXCHANGE AMOUNT=000000000016300000USD EXCHANGE RATE=000001000000000 USD AMOUNT=000000000016300000 VALUE DATE=2025/11/26 COMM CHARGE=00000000 SRC=FIOF448425112609001500 SBR=OLBB20251126704+ 0 PLANO,TX,75093 US /AC-000003886256DD028 IBK=Wells Fargo Bank NA 375 PARK AVE NEW YORK CITY NY 10152 US /BC-PNBPUS3N NYC BBK=BANCO DE LA PRODUCCION, S.A. AV. AMAZONAS N35-211 Y JAPON QUITO PICHINC HA EC /BC-PRODECEQ BNF=MARTHA MOSQUERA NOTPROVIDED /AC-12673051647 OBI=ECUADOR CONTRACT""")

    print(json.dumps(result, indent=2))