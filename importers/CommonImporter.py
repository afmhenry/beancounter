# might try to make common helper functions here
from decimal import Decimal




def stringToDecimal(str_num):
    if str_num is not '':
        return Decimal(str_num.replace(".", "").replace(",", "."))
    else:
        return Decimal("0")


def stringToFloatString(str_num):
    if str_num is not '':
        str_num_to_float = float(str_num.replace(".", "").replace(",", "."))
        return '{:.2f}'.format(str_num_to_float)
    else:
        return "0.00"


def floatToString(fl):
    return '{:.2f}'.format(fl)


def stringToFloat(str_fl):
    return float(str_fl.replace(".", "").replace(",", "."))

