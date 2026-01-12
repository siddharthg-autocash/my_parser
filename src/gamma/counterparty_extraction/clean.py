import spacy
import re

nlp = spacy.load("en_core_web_md")

LEGAL_SUFFIXES = {
    "LLC", "L.L.C",
    "INC", "INC.",
    "LTD", "LTD.",
    "LLP",
    "CORP", "CORPORATION",
    "CO", "CO.",
    "COMPANY",
    "HOLDINGS", "GROUP"
}

O_MARKER_RE = re.compile(r"O/\d*/|O/")

STOP_WORDS = {
    "NOTPROVIDED", "NA", "N/A", "UNKNOWN", "UNAVAILABLE"
}

def getEntity(text):
    if not text or not text.strip():
        return None

    # light normalization1 - split some delims
    for delim in ["*", "-"]:
        text = text.replace(delim, " ")
    text = re.sub(r"\s+", " ", text).strip()

    # light normalization2 - strip leading alphanumeric garbage shite
    tokens = text.split()
    i = 0
    while i < len(tokens):
        t = tokens[i]
        if any(c.isdigit() for c in t):
            i += 1
        else:
            break

    if i > 0 and i < len(tokens):
        text = " ".join(tokens[i:])

    doc = nlp(text)

    original_tokens = doc.text.split()

    
    # 1. ORG via legal suffix (end-anchored)
    for i in range(len(doc) - 1, -1, -1):
        tok = doc[i]

        if tok.text.upper() in LEGAL_SUFFIXES:
            start = i
            j = i - 1

            while j >= 0:
                t = doc[j]

                if t.like_num:
                    break
                if t.is_punct and t.text not in {",", "&", "."}:
                    break
                if t.ent_type_ in {"GPE", "DATE", "CARDINAL"}:
                    break
                if t.text.isalnum() and not t.text.isalpha():
                    break

                start = j
                j -= 1

            span = doc[start:i + 1]
            if len(span) >= 2:
                return span.text

    
    # 2. Name before O/ marker
    m = O_MARKER_RE.search(doc.text)
    if m:
        before = doc.text[:m.start()].strip().split()

        name_tokens = []
        for t in reversed(before):
            if t.isalpha():
                name_tokens.append(t)
            else:
                break

        name_tokens.reverse()

        # trim trailing non-name tokens using spaCy
        while name_tokens:
            last = name_tokens[-1]
            for tok in doc:
                if tok.text == last and tok.ent_type_ in {"GPE", "LOC", "DATE", "CARDINAL"}:
                    name_tokens.pop()
                    break
            else:
                break

        if name_tokens:
            return " ".join(name_tokens)

    
    # 3. Name before STOP words or slash
    parts = doc.text.split()

    for i, tok in enumerate(parts):
        if tok in STOP_WORDS or tok == "/":
            before = parts[:i]

            name_tokens = []
            for t in reversed(before):
                if t.isalpha():
                    name_tokens.append(t)
                else:
                    break

            name_tokens.reverse()

            while name_tokens:
                last = name_tokens[-1]
                for tok2 in doc:
                    if tok2.text == last and tok2.ent_type_ in {"GPE", "LOC", "DATE", "CARDINAL"}:
                        name_tokens.pop()
                        break
                else:
                    break

            if name_tokens:
                return " ".join(name_tokens)

    
    # 4. spaCy fallback (MONOTONIC — never shrink)
    for ent in doc.ents:
        if ent.label_ in {"ORG", "PERSON"}:
            if len(ent.text.split()) >= len(original_tokens):
                return ent.text

    
    # 5. Final fallback: keep clean alpha-only name
    if len(original_tokens) >= 2 and all(t.isalpha() for t in original_tokens):
        return doc.text

    return None
