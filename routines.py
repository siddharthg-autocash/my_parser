import json
import re
from pathlib import Path

def routine1(hitl,fmt:str):
    print(f'NEW KEY-VALUE PAIRS DETECTED.')
    print(f'ADD THEM TO THE {fmt} LIST')
    for key in hitl[1]:
            print(f'{key} : {hitl[1][key]}')
    print()



def routine2(canonical_key: str, val_name: str, fmt: str, inline: bool = False):

    canonical_key = canonical_key.strip().lower()
    val = val_name.strip()
    if not canonical_key or not val:
        return

    val_upper = val.upper()
    project_root = Path(__file__).resolve().parent

    # ---------- update canonical_keys.json ----------
    canonical_path = project_root / "key_engine" / "canonical_keys.json"
    with open(canonical_path, "r", encoding="utf-8") as f:
        canonical = json.load(f)

    canonical.setdefault(canonical_key, [])
    if val.lower() not in canonical[canonical_key]:
        canonical[canonical_key].append(val.lower())
        with open(canonical_path, "w", encoding="utf-8") as f:
            json.dump(canonical, f, indent=2)

    # ---------- append to format-specific keys ----------
    fmt_keys_path = project_root / "parsers" / fmt / "keys.py"
    _append_to_keys_py(fmt_keys_path, val_upper, inline)

    # ---------- append to parsers/all/keys.py ----------
    if fmt.lower() != "unknown":
        all_keys_path = project_root / "parsers" / "all" / "keys.py"
        _append_to_keys_py(all_keys_path, val_upper, inline)


def _append_to_keys_py(keys_path: Path, val_upper: str, inline: bool):
    text = keys_path.read_text(encoding="utf-8")
    target = "INLINE_KEYS" if inline else "KEYS"

    start = text.find(f"{target} = [")
    if start == -1:
        raise RuntimeError(f"{target} list not found in {keys_path}")

    open_bracket = text.find("[", start)
    close_bracket = text.find("]", open_bracket)

    if open_bracket == -1 or close_bracket == -1:
        raise RuntimeError(f"Malformed {target} list in {keys_path}")

    # extract list body
    body = text[open_bracket + 1 : close_bracket]

    # parse values
    values = []
    for item in body.split(","):
        item = item.strip().strip("'").strip('"')
        if item:
            values.append(item)

    # add if missing
    if val_upper not in values:
        values.append(val_upper)

    # dedupe + sort DESC by length
    values = sorted(set(values), key=lambda x: (-len(x), x))

    # rebuild list (pretty)
    rebuilt = f"{target} = [\n"
    for v in values:
        rebuilt += f'    "{v}",\n'
    rebuilt += "]"

    # replace old list
    new_text = text[:start] + rebuilt + text[close_bracket + 1 :]

    keys_path.write_text(new_text, encoding="utf-8")

