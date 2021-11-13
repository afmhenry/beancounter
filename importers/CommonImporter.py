# might try to make common helper functions here
from decimal import Decimal
import xlrd
import csv
import datetime
from beancount.core import data


def createAccountIfMissing(account_name, known_accounts, ticker, trans_date, meta):
    if account_name not in known_accounts:
        data_obj = data.Open(meta,
                             trans_date + datetime.timedelta(days=-1),
                             account_name,
                             [ticker],
                             None
                             )

        known_accounts.append(account_name)
        return True, data_obj, known_accounts
    else:
        return False, None, None


def stringToDecimalFromDA(str_num):
    if str_num != '':
        return Decimal(str_num.replace(".", "").replace(",", "."))
    else:
        return Decimal("0")


def stringToDecimalFromUS(str_num):
    if str_num != '':
        return Decimal(str_num)
    else:
        return Decimal("0")


def stringToFloatString(str_num):
    if str_num != '':
        str_num_to_float = float(str_num.replace(".", "").replace(",", "."))
        return '{:.2f}'.format(str_num_to_float)
    else:
        return "0.00"


def floatToString(fl):
    return '{:.2f}'.format(fl)


def stringToFloat(str_fl):
    return float(str_fl.replace(".", "").replace(",", "."))
