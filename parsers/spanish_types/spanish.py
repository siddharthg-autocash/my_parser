from parsers.spanish_types.pattern1 import is_pattern1, parse_pattern1
from parsers.spanish_types.pattern2 import is_pattern2, parse_pattern2
from parsers.spanish_types.pattern3 import is_pattern3, parse_pattern3
from parsers.spanish_types.pattern4 import is_pattern4, parse_pattern4
from parsers.spanish_types.pattern5 import is_pattern5, parse_pattern5
from parsers.spanish_types.pattern6 import is_pattern6, parse_pattern6
from parsers.spanish_types.pattern7 import is_pattern7, parse_pattern7
from parsers.spanish_types.pattern8 import is_pattern8, parse_pattern8
from parsers.spanish_types.pattern9 import is_pattern9, parse_pattern9
from parsers.spanish_types.pattern10 import is_pattern10, parse_pattern10
from parsers.spanish_types.pattern11 import is_pattern11, parse_pattern11
from parsers.spanish_types.pattern12 import is_pattern12, parse_pattern12


def is_spanish(line: str) -> int | None:
    if not line:
        return None

    line = line.strip()
    if not line:
        return None

    if is_pattern1(line):
        return 1
    if is_pattern2(line):
        return 2
    if is_pattern3(line):
        return 3
    if is_pattern4(line):
        return 4
    if is_pattern5(line):
        return 5
    if is_pattern6(line):
        return 6
    if is_pattern7(line):
        return 7
    if is_pattern8(line):
        return 8
    if is_pattern9(line):
        return 9
    if is_pattern10(line):
        return 10
    if is_pattern11(line):
        return 11
    if is_pattern12(line):
        return 12

    return None

def spanish_parse(line: str) -> dict | None:
    
    pat_no = is_spanish(line)
    print(f"Spanish Pattern-{pat_no}\n")

    if pat_no == 1:
        return parse_pattern1(line)
    if pat_no == 2:
        return parse_pattern2(line)
    if pat_no == 3:
        return parse_pattern3(line)
    if pat_no == 4:
        return parse_pattern4(line)
    if pat_no == 5:
        return parse_pattern5(line)
    if pat_no == 6:
        return parse_pattern6(line)
    if pat_no == 7:
        return parse_pattern7(line)
    if pat_no == 8:
        return parse_pattern8(line)
    if pat_no == 9:
        return parse_pattern9(line)
    if pat_no == 10:
        return parse_pattern10(line)
    if pat_no == 11:
        return parse_pattern11(line)
    if pat_no == 12:
        return parse_pattern12(line)

    return None
