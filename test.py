#!/usr/bin/env python3
import sys
import re

import PyPDF4
from beancount.core.number import D
from beancount.ingest import importer
from beancount.core import amount
from beancount.core import flags
from beancount.core import data

from datetime import date
from dateutil.parser import parse
import datetime
from importers.CommonImporter import *

# print(getCurrentStockPrice("TRYG"))

# price_tuple = getCurrentStockPrice("XDWM")  # (parse("2020-11-21").date(), '363.95')
# price_tuple = (parse("2020-11-21").date(), '363.95')
# meta = data.new_metadata("foo", 1)

# print(getTickersWithPriceStatusInLast10Days())
# print(fromAccountsGetTickers(getAccounts()))

# print(data.Price(meta, price_tuple[0], "XDWM", amount.Amount(D(price_tuple[1]), "DKK")))

# data.Price(None, "2020-20-20", "DKK", amount.Amount(D(1), "DKK"))

# print(formatMarketstackDate("2021-11-18T00:00:00+0000"))
# print(convertEuroToDKK())

from tika import parser  # pip install tika


def danishToStdDec(value):
    return Decimal(
        value.replace("-", "")
            .replace(".", "")
            .replace(",", ".")
    )


raw = parser.from_file('data/Lønseddel 01.12.2021-31.12.2021     Saxo Bank AS.PDF')
all_info = str.split(raw['content'], "Sats       Beløb")[1].split("AM-grundlag")[0]
lines = str.splitlines(all_info)

gross_pay = re.findall("[0-9]{2}\.[0-9]{3},[0-9]{2}", lines[1])[0]
gross_pay = danishToStdDec(gross_pay)
print(gross_pay)

firm_pension_contribution = re.findall("[0-9]\.[0-9]{3},[0-9]{2}", lines[8])[0]
firm_pension_contribution = danishToStdDec(firm_pension_contribution)
firm_pension_contribution_percentage = re.findall("[0-9]{2},[0-9]{2}", lines[8])[2]
firm_pension_contribution_percentage = danishToStdDec(firm_pension_contribution_percentage)

print(firm_pension_contribution, firm_pension_contribution_percentage)

own_pension_contribution = re.findall("[0-9]\.[0-9]{3},[0-9]{2}-", lines[9])[0]
own_pension_contribution = danishToStdDec(own_pension_contribution)

own_pension_contribution_percentage = re.findall("[0-9],[0-9]{2}", lines[9])[1]
own_pension_contribution_percentage = danishToStdDec(own_pension_contribution_percentage)

print(own_pension_contribution, own_pension_contribution_percentage)

am_bidrag = re.findall("[0-9]\.[0-9]{3},[0-9]{2}-", lines[13])[0]
am_bidrag = danishToStdDec(am_bidrag)
a_bidrag_base = re.findall("[0-9]{2}\.[0-9]{3},[0-9]{2}", lines[13])[0]
a_bidrag_base = danishToStdDec(a_bidrag_base)
am_bidrag_percentage = re.findall("[0-9],[0-9]{2}", lines[13])[1]
am_bidrag_percentage = danishToStdDec(am_bidrag_percentage)

print(am_bidrag, a_bidrag_base, am_bidrag_percentage)

a_skat = re.findall("[0-9]{2}\.[0-9]{3},[0-9]{2}-", lines[14])[0]
a_skat = danishToStdDec(a_skat)

a_skat_base = re.findall("[0-9]{2}\.[0-9]{3},[0-9]{2}", lines[14])[0]
a_skat_base = danishToStdDec(a_skat_base)

a_skat_fradrag = re.findall("[0-9]\.[0-9]{3},[0-9]{2}", lines[14])[1]
a_skat_fradrag = danishToStdDec(a_skat_fradrag)

a_skat_percentage = re.findall("[0-9]{2},[0-9]{2}", lines[14])[2]
a_skat_percentage = danishToStdDec(a_skat_percentage)

print(a_skat, a_skat_base, a_skat_fradrag, a_skat_percentage)

frokost_ordning = re.findall(" [0-9]{3},[0-9]{2}-", lines[15])[0]
frokost_ordning = danishToStdDec(frokost_ordning)

print(frokost_ordning)

net_pay = re.findall("[0-9]{2}\.[0-9]{3},[0-9]{2}", lines[25])[0]
net_pay = danishToStdDec(net_pay)
print(net_pay)

date_of_deposit = re.findall("[0-9]{2}-[0-9]{2}-[0-9]{4}", lines[25])[0]
date_of_deposit = datetime.datetime.strptime(date_of_deposit, "%d-%m-%Y").strftime("%Y-%m-%d")

