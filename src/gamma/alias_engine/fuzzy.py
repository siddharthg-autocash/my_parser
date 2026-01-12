from rapidfuzz import fuzz
import jellyfish

def score(a: str, b: str) -> float:
    if not a or not b:
        return 0.0

    a = a.upper().strip()
    b = b.upper().strip()

    jw = jellyfish.jaro_winkler_similarity(a, b)
    ts = fuzz.token_sort_ratio(a, b) / 100.0
    tset = fuzz.token_set_ratio(a, b) / 100.0

    return 0.34 * jw + 0.33 * ts + 0.33 * tset
