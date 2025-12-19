# Bank Parser Engine  

A deterministic, rule-based engine that normalizes and parses unstructured bank transaction narratives into structured JSON.  
Supports real-world formats including ACH, WIRE, SWIFT, vendor payments, processor EFT, PayPal, disbursements, funds transfers, direct debits, invoices, web/card payments, merchant references, and more.

---

## 📂 Project Structure  

```
│   README.md
│   routines.py                     # HITL + schema evolution
│   script.py                       # CLI + programmatic entry
│   util.py                         # Normalization + helpers
│
├───key_engine
│       canonical_keys.json         # Persisted semantic keys
│       key_detector.py             # Canonical key recognizer
│
├───parsers
│   │   __init__.py
│   │
│   ├───ach
│   │       ach_parser.py
│   │       keys.py
│   │       __init__.py
│   │
│   ├───all
│   │       all_parser.py
│   │       keys.py
│   │       __init__.py
│   │
│   ├───avidpay
│   │       avidp_check_parser.py
│   │       avidp_gen_parser.py
│   │
│   ├───directdebit
│   │       directdeb.py
│   │
│   ├───disbursement
│   │       disb_parser.py
│   │
│   ├───fundsTransfer
│   │       fundsTrans_parser.py
│   │
│   ├───merchref
│   │       merch_ref_parser.py
│   │
│   ├───misc
│   │       cardp.py
│   │       invo.py
│   │       webt.py
│   │
│   ├───paypal
│   │       paypal.py
│   │
│   ├───processor_eft
│   │       peft.py
│   │
│   ├───remittance
│   │       remi.py
│   │
│   ├───swift
│   │       swift_parser.py
│   │       keys.py
│   │
│   ├───vendorpay
│   │       vp_parser.py
│   │
│   ├───vendorpymt
│   │       vpymt_parser.py
│   │
│   ├───wire
│   │       wire_parser.py
│   │       keys.py
│   │
│   └───__init__.py (cache files omitted)
│
└───__pycache__ (auto-generated, ignored)
```

---

## 🧠 What It Does  

### 1️⃣ Normalize  
Every narrative string is cleaned, standardized, and made regex-safe:  
- Trim leading/trailing punctuation + pipes  
- Collapse multi-spaces  
- Uppercase everything  
- Normalize delimiter spacing around `: , = ; # \`  
- Remove narrative noise  

### 2️⃣ Identify  
Regex-based classifier determines narrative family:

- Vendor payment (RMR, remit, invoice, generic vendor)
- ACH / WIRE / SWIFT scoring
- PayPal (RDC, ACH return, general)
- Processor EFT
- Direct debit
- Merchant reference
- Web transfer
- Card processor
- Funds transfer
- Disbursement
- Invoice reference
- Unknown fallback (META)

### 3️⃣ Parse  
Format-aware extractors return structured JSON.  

---

## 🚀 Quick Start  

### Install  
```bash
pip install -e .
```

### CLI  
```bash
python script.py
```

### Programmatic  
```python
from script import parse

parsed, fmt = parse("AC-PROVIDENCE CONDO-VENDORPYMT RMR*IV*00028797**50.00\")
print(parsed)   # dict
print(fmt)      # format / type label
```

---

## 📘 Normalization Guarantees  

- `"   abc   "` → `"ABC"`
- `"\,|ABC|,,"` → `"ABC"`
- `"A  B   C"` → `"A B C"`
- `"ABC:123"` → `"ABC : 123"`
- `"abc\def"` → `"ABC \ DEF"`

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

## 📞 Maintainer  
Siddharth  
