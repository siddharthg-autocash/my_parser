# Bank Parser Engine

A rule-based engine to **standardize and parse unstructured bank transaction narratives**
(ACH, WIRE, SWIFT, like formats).

---

## High-level flow

1. **Input**: Raw transaction narrative (string)
2. **Normalization**:
   - Lowercasing
   - Whitespace normalization
   - Space insertion around delimiters (`: , = ; #`)
3. **Canonical key detection**:
   - Sliding window matching
   - Fuzzy matching against known variants
4. **Conflict resolution**:
   - Resolves overlaps
   - Prefers longer / higher-confidence matches
5. **Narrative rewrite**:
   - Replaces raw keys with canonical keys
6. **HITL trigger (only if needed)**:
   - Detects *new semantic keys only*
   - Ignores suffix fragments, numeric junk, value tokens
7. **Format detection**:
   - ACH / WIRE / SWIFT / fallback
8. **Format-specific parsing**:
   - Extracts structured fields into JSON
9. **Schema evolution (optional)**:
   - Approved keys are appended to:
     - `canonical_keys.json`
     - `parsers/{fmt}/keys.py`
     - `parsers/all/keys.py`

---

## What the system intentionally avoids

- Blind ML extraction
- Auto-learning without human approval
- Polluting schema with fragments like `NAME`, `ID`, `11`
- Overwriting or guessing values
- Non-deterministic behavior

---

## Project structure

```
.
├── script.py
├── util.py
├── routines.py
│
├── key_engine/
│   ├── key_detector.py
│   └── canonical_keys.json
│
├── parsers/
│   ├── ach/
│   ├── wire/
│   ├── swift/
│   └── all/
│
└── pyproject.toml
```

---

## How to run

### Install

```bash
pip install -e .
```

### Run

```bash
python script.py
```

### Programmatic usage

```python
from script import parse
output, fmt = parse(narrative)
```

---

## HITL behavior

- Triggered only for **new semantic keys**
- Suggests up to **4 words of left-context**
- Stops at delimiters
- Approved keys are persisted via `routine2()`
- Future runs auto-detect the key

---

## Future work

### Value cleaning (post-parsing)

- Date normalization
- Amount normalization
- Account masking
- Name and address cleanup
- ID validation

## One-line summary

A deterministic, human-in-the-loop engine to standardize and parse bank transaction narratives while safely evolving its schema. 
