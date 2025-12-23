import json
from util import detect_format, normalize_spaces
from parsers.wire.wire_parser import wire_parser
from parsers.ach.ach_parser import ach_parser
from parsers.swift.swift_parser import swift_parser
from parsers.all.all_parser import all_parser

from key_engine.key_detector import KeyDetector
from routines import routine1, routine2

import numpy as np
import pandas as pd

from additionalFmts import route_to_additional_format
from extract_payer_payee import extract_payor_payee

key_detector = KeyDetector()


def parse(narr: str):

    fmt = detect_format(narr)
    print(f"\nFORMAT IDENTIFIED: {fmt}")

    parsed, routed_fmt = route_to_additional_format(fmt, narr)
    if routed_fmt:
        return parsed, routed_fmt
    
    narr = normalize_spaces(narr)
    rewritten_narr, hitl = key_detector.rewrite(narr)

    if hitl:
        routine1(hitl, fmt)

    if fmt == 'wire':
        output = wire_parser(rewritten_narr)
    elif fmt == 'ach':
        output = ach_parser(rewritten_narr)
    elif fmt == 'swift':
        output = swift_parser(rewritten_narr)
    else:
        output = all_parser(rewritten_narr)

    return output, fmt

def CTPTY(narr: str, amount: float | None = None):
    final = {}
    output, fmt = parse(narr)
    res = extract_payor_payee(
        output,
        amount=amount
    )
    final["ctpty"] = res
    final["parsed"] = output
    return final, fmt

if __name__=='__main__':
    pass