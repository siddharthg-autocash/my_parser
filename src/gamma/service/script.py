import json
from typing import Optional
from project_gamma.src.gamma.util.route import route_to_parser
from project_gamma.src.gamma.counterparty_extraction.extract_payer_payee import extract_payor_payee

ALLOWED_BAI_CODES = {
    "145", "455", "195", "495", "508",
    "208", "169", "469", "493", "-NTR"
}

def parse(narr: str):
    out, fmt = route_to_parser(narr)
    return out, fmt

def CTPTY(narr: str,amount: Optional[float] = None,bai_code: Optional[str] = None):
    
# i will be commenting this bai checking logic for now 
    # if bai_code and bai_code not in ALLOWED_BAI_CODES:
    #     return {
    #         "error": f"BAI code {bai_code} not supported for CTPTY extraction"
    #     }, None

    final = {}
    out, fmt = parse(narr)
    res = extract_payor_payee(out, amount=amount,narrative=narr)
    final["ctpty"] = res
    final["parsed"] = out
    return final, fmt
