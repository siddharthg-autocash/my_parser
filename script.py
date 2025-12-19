import json
from util import detect_format, normalize_spaces
from parsers.wire.wire_parser import wire_parser
from parsers.ach.ach_parser import ach_parser
from parsers.swift.swift_parser import swift_parser
from parsers.all.all_parser import all_parser

from key_engine.key_detector import KeyDetector
from routines import routine1,routine2

import numpy as np
import pandas as pd

from parsers.disbursement.disb_parser import parse_disbursement_narrative
from parsers.fundsTransfer.fundsTrans_parser import parse_funds_transfer_frmdep
from parsers.vendorpay.vp_parser import parse_vendor_pay_narrative
from parsers.vendorpymt.vpymt_parser import parse_vendor_payment_rmr,parse_vendor_payment_remittance
from parsers.avidpay.avidp_check_parser import parse_avidpay_check
from parsers.avidpay.avidp_gen_parser import parse_avidpay_generic
from parsers.misc.cardp import parse_card_payment
from parsers.misc.invo import parse_invoice_reference
from parsers.misc.webt import parse_web_transfer
from parsers.remittance.remi import parse_remittance_advice
from parsers.merchref.merch_ref_parser import parse_merchant_reference
from parsers.paypal.paypal import parse_paypal
from parsers.processor_eft.peft import parse_processor_eft
from parsers.directdebit.directdeb import parse_direct_debit

key_detector = KeyDetector()

def parse(narr: str):

    fmt = detect_format(narr)
    print(f"\nFORMAT IDENTIFIED: {fmt}")

    if(fmt=='disbursement'): return parse_disbursement_narrative(narr),fmt
    elif(fmt=='fundstr'): return parse_funds_transfer_frmdep(narr),fmt
    elif(fmt=='vpay'): return parse_vendor_pay_narrative(narr),fmt
    elif(fmt=='vpymt'): return parse_vendor_payment_rmr(narr),fmt
    elif(fmt=='vpay_remit'): return parse_vendor_payment_remittance(narr),fmt
    elif(fmt=='avp_check'): return parse_avidpay_check(narr),fmt
    elif(fmt=='avp_gen'): return parse_avidpay_generic(narr),fmt
    elif(fmt=='card'): return parse_card_payment(narr),fmt
    elif(fmt=='invo'): return parse_invoice_reference(narr),fmt
    elif(fmt=='webt'): return parse_web_transfer(narr),fmt
    elif(fmt=='remi'): return parse_remittance_advice(narr),fmt
    elif(fmt=='merch'): return parse_merchant_reference(narr),fmt
    elif fmt.startswith("PAYPAL"): return parse_paypal(narr), fmt
    elif(fmt=='peft'): return parse_processor_eft(narr),fmt
    elif (fmt == 'ddbt'): return parse_direct_debit(narr), fmt
    
    narr = normalize_spaces(narr)
    rewritten_narr,hitl = key_detector.rewrite(narr)

    if(hitl): routine1(hitl,fmt)        

    if fmt == 'wire':
        output = wire_parser(rewritten_narr)
    elif fmt == 'ach':
        output = ach_parser(rewritten_narr)
    elif fmt == 'swift':
        output = swift_parser(rewritten_narr)
    else:
        output = all_parser(rewritten_narr)

    return output,fmt



if __name__ == '__main__':    
    pass

