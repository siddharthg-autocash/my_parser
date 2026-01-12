# Project Gamma

Project Gamma is a **deterministic, rule-based bank transaction narrative parsing engine** that converts unstructured bank statement descriptions into **structured, auditable JSON**.

It performs **format detection**, **rule-driven parsing**, **payer/payee (counterparty) extraction**, and **approval-based alias resolution**, and exposes results via **Python**, **FastAPI**, and an interactive **Streamlit UI**.

---

## Key Characteristics

- Fully deterministic (no probabilistic behavior)
- Rule-driven and explainable
- Auditable outputs
- Explicit approval for ambiguous entity resolution
- Designed for continuous rule evolution

---

## Important Notes

**Note 1**  
The engine reliably extracts structured key–value data. Counterparty extraction is intentionally conservative and continues to evolve through rules and approvals.

**Note 2**  
If a narrative is parsed incorrectly, the correct fix is to **change or add rules**, not to tune probabilities or thresholds.

---

## Overview

Real-world bank transaction narratives are inconsistent, delimiter-heavy, and highly format-dependent.

Project Gamma was built to parse these narratives **without machine learning**, ensuring that:

- every decision is explainable,
- every failure is fixable through rules,
- and no output is produced without justification.

Given a raw narrative string, the engine produces:

- a normalized narrative,
- a detected transaction format,
- structured key–value data,
- resolved payer and payee (CTPTY),
- optional canonical entity mapping via aliases.

The architecture is intentionally **non-probabilistic**:

- No ML models  
- No silent assumptions  
- No schema drift  
- No hallucinated entities  

---

## What the Engine Does

For each transaction narrative, Project Gamma executes the following pipeline:

1. Normalize the narrative  
2. Identify the transaction format  
3. Parse structured fields  
4. Extract payer and payee (CTPTY)  
5. Optionally resolve canonical aliases (approval-based)  
6. Expose results via CLI, Python, API, or UI  

Each stage is isolated, deterministic, and independently extensible.

---

## 1. Narrative Normalization

All narratives are normalized before classification or parsing.

### Normalization guarantees

- Uppercases text  
- Removes leading/trailing punctuation  
- Collapses repeated whitespace  
- Normalizes delimiter spacing (`: , = ; # \\`)  
- Produces regex-safe input  

### Example transformations

```
"   <TEXT>   "        → "<TEXT>"
"│,<TEXT>,│"          → "<TEXT>"
"A   B     C"         → "A B C"
"KEY:VALUE"           → "KEY : VALUE"
"ABC\\DEF"            → "ABC \\ DEF"
```

---

## 2. Format Identification

After normalization, the engine deterministically identifies the transaction family using ordered rule checks.

Supported formats include (non-exhaustive):

- ACH  
- WIRE  
- SWIFT  
- Processor EFT  
- Vendor payments  
- Disbursements  
- Direct debit  
- Funds transfer / sweep  
- PayPal  
- Merchant reference  
- Remittance  
- Card / invoice / misc  
- LATAM (language- and pattern-specific parsing)  
- Generic fallback (`ALL`)  

Each narrative is routed to **exactly one parser**.

---

## 3. Structured Parsing

Each format has a dedicated parser responsible for **fact extraction only**.

### Parser guarantees

- Extracts only what is explicitly present  
- Preserves raw values  
- Does not infer payer or payee  
- Does not infer transaction direction  
- Does not apply business logic  

Typical extracted fields include:

- Entity names  
- Account identifiers  
- Reference numbers  
- Dates and timestamps  
- Transaction codes  
- Bank identifiers  
- Free-form descriptions  

All parsers return **plain dictionaries**.

---

## 4. Key Evolution (Controlled Scope)

Key evolution applies only to formats with strong delimiter behavior:

- ACH  
- WIRE  
- SWIFT  
- ALL (generic fallback)  

These formats allow **safe detection of new semantic keys**.

### How key evolution works

- Unknown keys are detected at parse time  
- Up to four words of left-context are proposed  
- Delimiters define key boundaries  
- Explicit approval is required  
- Approved keys are persisted canonically  

Other formats use fixed schemas and do not participate in key evolution.

---

## 5. Counterparty Resolution (CTPTY)

Counterparty extraction runs **after parsing** and consumes structured parser output.

It produces:

- `payer`
- `payee`
- `amount`

### Resolution principles

- Explicit semantic roles always win  
- Account-like values are normalized as `BANK(<id>)`  
- Partial information is preserved  
- Inference is minimal and rule-bound  
- Unknown roles remain unknown  

No guessing. No hallucination.

---

## 6. Alias Engine (Canonical Entity Resolution)

The Alias Engine resolves raw payer/payee strings into canonical entities.

It operates **after CTPTY extraction** and is fully decoupled from parsing.

### What the Alias Engine does

- Normalizes raw counterparty strings  
- Performs fuzzy matching against a master list  
- Uses weighted similarity scoring  
- Surfaces top-K candidates  
- Requires explicit approval before persistence  
- Stores aliases permanently for reuse  

### What it does NOT do

- It does not guess during parsing  
- It does not modify raw parser output  
- It does not run automatically without approval  

Alias resolution is always **explicit and auditable**.

---

## 7. Streamlit Interface

A Streamlit UI is provided for interactive review and approval.

The UI allows users to:

- Paste narratives or JSON input  
- Run full parse + CTPTY extraction  
- Review structured output  
- Inspect top-K alias matches  
- Manually approve or create aliases  
- Persist canonical mappings safely  

---

## Interfaces

### CLI

```bash
python script.py
```

### Python API

```python
from script import parse, CTPTY

parsed, fmt = parse("<NARRATIVE>")
result, fmt = CTPTY("<NARRATIVE>", amount=<SIGNED_AMOUNT>)
```

### FastAPI Service

```bash
uvicorn api:app --reload
```

### Streamlit Servie (Preferred)

```bash
PYTHONPATH=. streamlit run project_gamma/experiments/streamlit_app.py
```

---

## Installation

```bash
pip install -r requirements.txt
```

---

## Project Structure (Relevant Files Only)

```
project-gamma/
│
├── data/
│
├── docs/
│
├── experiments/
│   └── streamlit_app.py
│
├── api/
│   └── api.py
│
├── src/
│   └── gamma/
│       ├── key_engine/
│       ├── alias_engine/
│       ├── parsers/
│       ├── extract_payer_payee.py
│       ├── route.py
│       ├── routine.py
│       ├── util.py
│       ├── script.py
│       └── requirements.txt
│    
└── README.md
```

---

## One-Line Summary

A deterministic, approval-driven engine for parsing bank transaction narratives into structured, auditable JSON with explainable counterparty extraction and alias resolution.

---

## Maintainer

Siddharth
