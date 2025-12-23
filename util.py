import re

from parsers.disbursement.disb_parser import is_disbursement_narrative
from parsers.fundsTransfer.fundsTrans_parser import is_funds_transfer_frmdep
from parsers.vendorpay.vp_parser import is_vendor_pay_narrative
from parsers.vendorpymt.vpymt_parser import is_vendor_payment_remittance,is_vendor_payment_rmr
from parsers.avidpay.avidp_check_parser import is_avidpay_check
from parsers.avidpay.avidp_gen_parser import is_avidpay_generic
from parsers.misc.cardp import is_card_payment
from parsers.misc.invo import is_invoice_reference
from parsers.misc.webt import is_web_transfer
from parsers.remittance.remi import is_remittance_advice
from parsers.merchref.merch_ref_parser import is_merchant_reference
from parsers.paypal.paypal import classify_paypal
from parsers.processor_eft.peft import is_processor_eft
from parsers.directdebit.directdeb import is_direct_debit

from parsers.spanish_types.spanish import is_spanish

def normalize_spaces(text: str) -> str:
    
    text = text.replace('.','')
    text = text.replace(',',' ')

    # add space BEFORE and AFTER delimiter if missing
    text = re.sub(r"(?<!\s)([:,=;#])", r" \1", text)
    text = re.sub(r"([:,=;#])(?!\s)", r"\1 ", text)

    return " ".join(text.split())


# KEYWORDS WITH WEIGHTS 

KEYWORDS = {
    "swift": [
        ("uetr", 4),("mt103", 4),("mt202", 4),("swift", 2),("bic", 2),("imad", 4),("omad", 4),("smad", 4),
    ],

    "ach": [
        ("ppd", 5),("ccd", 5),("ctx", 5),("web", 4),("tel", 4),("trace number", 5),("trace no", 5),("entry class", 5),("orig co name", 5),("company id", 1),("effective date", 1),("ach", 2),
    ],

    "wire": [
        ("fed ref", 3),("fed", 2),("aba", 3),("routing number", 3),("wire type", 3),("service ref", 2),("sent at", 1),("received at", 1),("obi", 2),("orf", 2),("srf", 2),("obk", 2),("ibk", 2),("sbk", 2),("bbk", 2),("bnf", 2),
    ]
}

PRIORITY = ["swift", "wire", "ach"]


def normalize_for_detect(text: str) -> str:
    text = text.lower()
    text = re.sub(r"[.,:/\-]", " ", text)
    return normalize_spaces(text)

def normalize_narrative(line: str) -> str:
    if not line: return ""
    line = re.sub(r"^[,\|]+", "", line)
    line = re.sub(r"[,\|\\]+$", "", line)
    line = re.sub(r"\s+", " ", line)
    return line.strip().upper()


# pre-classify

def preClassify(text: str) -> str:
    
    if is_spanish(text)!=None:
        return 'spanish'

    if classify_paypal(text)!=None:
        return classify_paypal(text) 
    
    if is_disbursement_narrative(text):
        return 'disbursement'

    if is_funds_transfer_frmdep(text):
        return 'fundstr'

    if is_vendor_payment_remittance(text):
        return "vpay_remit"

    if is_vendor_payment_rmr(text):     
        return 'vpymt'

    if is_vendor_pay_narrative(text):
        return 'vpay'

    if is_avidpay_check(text):
        return 'avp_check'
    
    if is_avidpay_generic(text):
        return 'avp_gen'
    
    if is_card_payment(text):
        return 'card'
    
    if is_invoice_reference(text):
        return 'invo'
    
    if is_web_transfer(text):
        return 'webt'
    
    if is_processor_eft(text):
        return "peft"
    
    if is_remittance_advice(text):
        return 'remi'
    
    if is_merchant_reference(text):
        return 'merch'
    
    if is_direct_debit(text):
        return 'ddbt'

    return 'done'


# FORMAT DETECTOR 

def detect_format(text: str) -> str:

    pc = preClassify(text)

    # --- HOLD FORMATS ---
    HOLD_LIST = {"peft", "avp_check", "avp_gen"}
    hold_flag = pc in HOLD_LIST

    # if pc is something else and not "done", return it normally
    if pc != "done" and not hold_flag:
        return pc

    # ----- SCORING SECTION -----
    t = normalize_for_detect(text)
    scores = {k: 0 for k in KEYWORDS}

    for fmt, items in KEYWORDS.items():
        for keyword, weight in items:
            if keyword in t:
                scores[fmt] += weight

    # HARD GUARD
    if "uetr" in t:
        return "swift"

    best = max(scores, key=lambda k: scores[k])

    # scoring failed → return held format
    if scores[best] < 3:
        if hold_flag:
            return pc
        return "unknown"

    # tie resolution
    tied = [k for k, v in scores.items() if v == scores[best]]
    for p in PRIORITY:
        if p in tied:
            return p

    return best


if __name__=='__main__':
    print(detect_format(input()))