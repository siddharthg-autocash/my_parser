# additionalFmts.py

from parsers.disbursement.disb_parser import parse_disbursement_narrative
from parsers.fundsTransfer.fundsTrans_parser import parse_funds_transfer_frmdep
from parsers.vendorpay.vp_parser import parse_vendor_pay_narrative
from parsers.vendorpymt.vpymt_parser import parse_vendor_payment_rmr, parse_vendor_payment_remittance
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
from parsers.spanish_types.spanish import spanish_parse


def route_to_additional_format(fmt: str, narr: str):

    if fmt == 'spanish':
        return spanish_parse(narr), fmt

    if fmt == 'disbursement':
        return parse_disbursement_narrative(narr), fmt

    if fmt == 'fundstr':
        return parse_funds_transfer_frmdep(narr), fmt

    if fmt == 'vpay':
        return parse_vendor_pay_narrative(narr), fmt

    if fmt == 'vpymt':
        return parse_vendor_payment_rmr(narr), fmt

    if fmt == 'vpay_remit':
        return parse_vendor_payment_remittance(narr), fmt

    if fmt == 'avp_check':
        return parse_avidpay_check(narr), fmt

    if fmt == 'avp_gen':
        return parse_avidpay_generic(narr), fmt

    if fmt == 'card':
        return parse_card_payment(narr), fmt

    if fmt == 'invo':
        return parse_invoice_reference(narr), fmt

    if fmt == 'webt':
        return parse_web_transfer(narr), fmt

    if fmt == 'remi':
        return parse_remittance_advice(narr), fmt

    if fmt == 'merch':
        return parse_merchant_reference(narr), fmt

    if fmt.startswith("PAYPAL"):
        return parse_paypal(narr), fmt

    if fmt == 'peft':
        return parse_processor_eft(narr), fmt

    if fmt == 'ddbt':
        return parse_direct_debit(narr), fmt

    return None, None
