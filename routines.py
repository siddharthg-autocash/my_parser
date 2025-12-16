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
    lines = keys_path.read_text(encoding="utf-8").splitlines()
    target = "INLINE_KEYS" if inline else "KEYS"

    start = end = None

    # locate list boundaries
    for i, line in enumerate(lines):
        if line.strip().startswith(f"{target}"):
            start = i
            continue
        if start is not None and line.strip() == "]":
            end = i
            break

    if start is None or end is None:
        raise RuntimeError(f"{target} list not found in {keys_path}")

    # extract existing values
    values = []
    for line in lines[start + 1 : end]:
        token = line.strip().strip(",").strip('"')
        if token:
            values.append(token)

    # exact duplicate check
    if val_upper in values:
        return

    # add + sort (DESC by length, then alpha)
    values.append(val_upper)
    values.sort(key=lambda x: (-len(x), x))

    # rebuild file
    new_lines = lines[: start + 1]
    for v in values:
        new_lines.append(f'    "{v}",')
    new_lines.extend(lines[end:])

    keys_path.write_text("\n".join(new_lines) + "\n", encoding="utf-8")
