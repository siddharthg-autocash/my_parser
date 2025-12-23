import re
from typing import Any, Dict, Optional


def extract_payor_payee(
    parsed: Dict[str, Any],
    customer_name = None,
    amount: Optional[float] = None
) -> Dict[str, Any]:

    # ---------------- helpers ----------------
    def norm(v):
        if v is None:
            return None
        if isinstance(v, dict):
            v = v.get("value") or v.get("name")
        s = str(v).strip()
        s = re.sub(r"\s+", " ", s)
        return s if s else None

    # normalize keys (case-insensitive)
    data = {k.lower(): v for k, v in parsed.items()}

    # ---------------- role maps ----------------
    PAYER_KEYS = [
        "orig co name", "originator", "orig", "org",
        "ordering customer", "ordering cust",
        "sender", "sending co name",
        "debtor", "paid to",
        "from acct", "from account",
        "entry desc", "company name", "comp name"
    ]

    PAYEE_KEYS = [
        "beneficiary", "bnf", "bn f",
        "receiver", "recv name", "receiver name",
        "creditor", "ulti bene",
        "individual or receiving company name",
        "customer name", "cust name"
    ]

    COUNTERPARTY_KEYS = [
        "counterparty", "counterparty_name",
        "entity", "related entity", "related party"
        ,"to_account"
        ,"from_account"
    ]

    payer = None
    payee = None

    # ---------------- PRIORITY 1: direct role mapping ----------------
    for k in PAYER_KEYS:
        if k in data:
            payer = norm(data[k])
            if payer:
                break

    for k in PAYEE_KEYS:
        if k in data:
            payee = norm(data[k])
            if payee:
                break

    if payer and payee:
        return {
            "payer": payer,
            "payee": payee,
            "amount": amount
        }

    # ---------------- PRIORITY 2: counterparty ----------------
    ctpty = None
    for k in COUNTERPARTY_KEYS:
        if k in data:
            ctpty = norm(data[k])
            if ctpty:
                break

    if ctpty:
        if amount is not None and amount < 0:
            return {
                "payer": customer_name,
                "payee": ctpty,
                "amount": amount
            }
        else:
            return {
                "payer": ctpty,
                "payee": customer_name,
                "amount": amount
            }

    # ---------------- PRIORITY 3: amount-only fallback ----------------
    if amount is not None:
        return {
            "payer": customer_name,
            "payee": customer_name,
            "amount": amount
        }

    # ---------------- FINAL fallback ----------------
    return {
        "payer": customer_name,
        "payee": customer_name,
        "amount": amount
    }
