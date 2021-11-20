#!/usr/bin/env python3
import sys
import re
from beancount.core.number import D
from beancount.ingest import importer
from beancount.core import amount
from beancount.core import flags
from beancount.core import data

from datetime import date
from dateutil.parser import parse
import datetime
from importers.CommonImporter import *

#print(getCurrentStockPrice("TRYG"))

#price_tuple = getCurrentStockPrice("XDWM")  # (parse("2020-11-21").date(), '363.95')
#price_tuple = (parse("2020-11-21").date(), '363.95')
#meta = data.new_metadata("foo", 1)

print(getTickersWithPriceStatusInLast10Days())
print(fromAccountsGetTickers(getAccounts()))

#print(data.Price(meta, price_tuple[0], "XDWM", amount.Amount(D(price_tuple[1]), "DKK")))

#data.Price(None, "2020-20-20", "DKK", amount.Amount(D(1), "DKK"))

# print(formatMarketstackDate("2021-11-18T00:00:00+0000"))
# print(convertEuroToDKK())
