import json
from util import detect_format, normalize_spaces
from parsers.wire.wire_parser import wire_parser
from parsers.ach.ach_parser import ach_parser
from parsers.swift.swift_parser import swift_parser
from parsers.all.all_parser import all_parser

from key_engine.key_detector import KeyDetector
from routines import routine1,routine2

key_detector = KeyDetector()

def parse(narr: str):

    narr = normalize_spaces(narr)
    rewritten_narr,hitl = key_detector.rewrite(narr)
    fmt = detect_format(rewritten_narr)

    if(hitl): routine1(hitl,fmt)
    # print(narr)
    print(f'format identified: {fmt}')

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
    narr = input()
    narr,fmt = parse(narr)
    val = json.dumps(narr, indent=3)
    print(val)
    # routine2('appended','FED. REF. NO.',fmt)
    # routine2('appended','B/O BANK',fmt)
    # routine2('appended','REC FROM',fmt)
