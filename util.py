import re

def normalize_spaces(text: str) -> str:
    text = text.replace('.','')
    text = text.replace(',',' ')

    # add space BEFORE delimiter if missing
    text = re.sub(r"(?<!\s)([:,=;#])", r" \1", text)

    # add space AFTER delimiter if missing
    text = re.sub(r"([:,=;#])(?!\s)", r"\1 ", text)

    # collapse extra spaces
    return " ".join(text.split())



# ===================================
# KEYWORDS WITH WEIGHTS (STRONG > WEAK)
# ===================================

KEYWORDS = {
    "swift": [
        ("uetr", 4),
        ("mt103", 4),
        ("mt202", 4),
        ("swift", 2),
        ("bic", 2),
        ("imad", 4),
        ("omad", 4),
        ("smad", 4),
    ],

    "ach": [
        ("ppd", 5),
        ("ccd", 5),
        ("ctx", 5),
        ("web", 4),
        ("tel", 4),
        ("trace number", 5),
        ("trace no", 5),
        ("entry class", 5),
        ("orig co name", 5),
        ("company id", 1),
        ("effective date", 1),
        ("ach", 2),
    ],

    "wire": [
        ("fed ref", 3),
        ("fed", 2),
        ("aba", 3),
        ("routing number", 3),
        ("wire type", 3),
        ("service ref", 2),
        ("sent at", 1),
        ("received at", 1),
        ("obi", 2),
        ("orf", 2),
        ("srf", 2),
        ("obk", 2),
        ("ibk", 2),
        ("sbk", 2),
        ("bbk", 2),
        ("bnf", 2),
    ]
}

PRIORITY = ["swift", "wire", "ach"]


def normalize_for_detect(text: str) -> str:
    text = text.lower()
    text = re.sub(r"[.,:/\-]", " ", text)
    return normalize_spaces(text)


# ============================================================
# FORMAT DETECTOR (SCORED + GUARDED)
# ============================================================

def detect_format(text: str) -> str:
    t = normalize_for_detect(text)

    scores = {k: 0 for k in KEYWORDS}

    for fmt, items in KEYWORDS.items():
        for keyword, weight in items:
            if keyword in t:
                scores[fmt] += weight

    # HARD GUARD: UETR implies SWIFT carriage
    if "uetr" in t:
        return "swift"

    best = max(scores, key=lambda k: scores[k])

    if scores[best] < 3:
        return "unknown"

    tied = [k for k, v in scores.items() if v == scores[best]]
    for p in PRIORITY:
        if p in tied:
            return p

    return best
