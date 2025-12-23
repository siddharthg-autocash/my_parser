# Bank Parser Engine

A **deterministic, rule-based bank transaction narrative parsing engine** that converts unstructured bank statement descriptions into **structured, auditable JSON**, with **counterparty (payer/payee) resolution**, **format detection**, and **API access**.

---

## Project Structure (Relevant Files Only)

```
|
|-- api.py
|-- additionalFmts.py
|-- extract_payer_payee.py
|-- routines.py
|-- script.py
|-- util.py
|
|-- key_engine
|   |-- canonical_keys.json
|   |-- key_detector.py
|
|-- parsers
|   |-- ach
|   |-- all
|   |-- avidpay
|   |-- directdebit
|   |-- disbursement
|   |-- fundsTransfer
|   |-- merchref
|   |-- misc
|   |-- paypal
|   |-- processor_eft
|   |-- remittance
|   |-- spanish_types
|   |-- swift
|   |-- vendorpay
|   |-- vendorpymt
|   |-- wire
```

---

## Overview

I built this engine to process raw transaction narratives and produce:

- A normalized narrative
- A detected transaction format
- Parsed key–value data
- Resolved payer and payee (CTPTY) -> Need help/review on
- Clear reasoning for every resolution decision

The architecture is intentionally **non-probabilistic**:
- No machine learning
- No silent assumptions
- No uncontrolled schema drift
- Every decision is rule-based and auditable

---

## What the Engine Does

Given a raw transaction narrative string, the engine performs the following steps:

1. **Normalize** the narrative
2. **Identify** the transaction family
3. **Parse** structured fields
4. **Resolve counterparties (CTPTY)**
5. **Expose results via CLI, Python API, or FastAPI**

Each step is isolated, deterministic, and testable.

---

## 1. Narrative Normalization

All narratives are normalized before any classification or parsing.

### Normalization guarantees

- Uppercases all text
- Removes leading/trailing punctuation and pipes
- Collapses multiple spaces
- Normalizes delimiters (`: , = ; # \\`)
- Produces regex-safe input

Illustrative examples (placeholders only):

```
"   <TEXT>   "        → "<TEXT>"
"|,<TEXT>,|"          → "<TEXT>"
"A   B     C"         → "A B C"
"KEY:VALUE"           → "KEY : VALUE"
"ABC\\DEF"             → "ABC \\ DEF"
```

---

## 2. Format Identification

After normalization, the engine **deterministically identifies** the transaction family using ordered regex rules.

Supported categories include (non-exhaustive):

- ACH
- WIRE
- SWIFT
- Vendor payments (multiple variants)
- Disbursements
- Processor EFT
- PayPal transactions
- Direct debit
- Funds transfer / sweep transfer
- Merchant reference
- Web transfer
- Card transactions
- Invoice references
- Language-specific patterns
- Generic fallback (`ALL`)

Each narrative is routed to **exactly one parser**.

---

## 3. Structured Parsing

Each format has a dedicated parser that extracts **facts only**.

### Parser guarantees

- Extracts fields exactly as present
- Preserves raw values
- Does **not** infer payer/payee
- Does **not** infer direction
- Does **not** apply business logic

Typical extracted fields include:
- Entity names
- Account identifiers
- Reference numbers
- Dates and timestamps
- Transaction codes
- Bank identifiers
- Free-form descriptions

All parsers return a plain dictionary.

---

## 4. Human-in-the-Loop (HITL) Key Evolution

HITL is intentionally limited in scope.

It applies **only** to the following parser families:

- ACH
- WIRE
- SWIFT
- ALL (generic fallback)

### What HITL does

When a previously unseen **semantic key** is detected in these formats:

- The engine pauses execution
- Suggests up to **four words of left-context**
- Stops at known delimiters
- Requests human approval
- Persists approved keys in a canonical store

Approved keys are reused automatically in future runs.

### Fuzzy key matching

For ACH / WIRE / SWIFT / ALL:

- Keys are matched **case-insensitively**
- Minor spacing and delimiter variations are tolerated
- Canonical forms are learned once and reused

Other formats use **fixed schemas only** and do not participate in HITL.

---

## 5. Counterparty Resolution (CTPTY)

Counterparty resolution is handled after from parsing, in:

This function resolves:

- `payer`
- `payee`
- `amount`

### Core principles

- Explicit semantic roles always win
- Direction never overrides known facts
- Case-insensitive key handling
- Nested values are safely resolved
- Output is always complete

### Resolution order

1. **Direct semantic mapping**
   - Originator-type keys → payer
   - Beneficiary-type keys → payee

2. **If both sides exist**
   - Resolution stops immediately

3. **If only one entity exists**
   - `amount < 0` → CUSTOMER paid
   - `amount > 0` → CUSTOMER received

4. **Counterparty / entity fallback**
   - Used only if explicit roles are missing

5. **Final fallback**
   - CUSTOMER → CUSTOMER

Every resolution includes a **reason code** for auditability.

---

## Interfaces

### CLI

Used for debugging, inspection, and HITL approval:

```bash
python script.py
```

---

### Python API

```python
from script import parse, CTPTY

parsed, fmt = parse("<NARRATIVE>")
result, fmt = CTPTY("<NARRATIVE>", amount=<SIGNED_AMOUNT>)
```

---

### FastAPI Service

A production-ready FastAPI service is included.

```bash
uvicorn api:app --reload
```

Endpoint:

```
POST /ctpty
```

Request body:

```json
{
  "narrative": "<TRANSACTION_NARRATIVE>",
  "amount": -12345.67
}
```

---

## Installation

All dependencies are declared in the project.

```bash
pip install -r requirements
```

---

## What This Engine Is Not

- No machine learning
- No probabilistic inference
- No silent assumptions
- No uncontrolled schema evolution
- No opaque decision making

---

## One-Line Summary

A deterministic, human-controlled engine for parsing and resolving real-world bank transaction narratives into structured, auditable JSON, with production-safe counterparty resolution and API access.

---

## Maintainer

Siddharth Gautam

