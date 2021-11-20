#!/usr/bin/env python3

from beancount.core.number import D
from beancount.ingest import importer
from beancount.core import amount
from ..CommonImporter import *
from dateutil.parser import parse
import os


class Importer(importer.ImporterProtocol):
    def __init__(self, source_account):
        self.source_account = source_account

    def identify(self, f):
        # we wont use the file--just the option to inject data to the beancount file
        if os.path.basename(f.name) == "get-stock-prices.txt":
            return True
        else:
            return False

    # Forgive me, for I have sinned
    # https://beancount.github.io/docs/beancount_design_doc.html#isolation-of-inputs
    # Definitely not following best practice here. But like making "importers" in the same way...

    def extract(self, f):

        entries = []
        skip_tickers = getTickersWithPriceStatusInLast10Days()
        i = 0
        ticker_list = fromAccountsGetTickers(getAccounts())

        # remove duplicates in case I have multiple accounts with same ticker
        ticker_existing = list(dict.fromkeys(ticker_list))
        ticker_update = [x for x in ticker_existing if x not in skip_tickers]

        for ticker in ticker_update:
            # i = i + 1
            meta = data.new_metadata(f.name, i)
            price_tuple = getCurrentStockPrice(ticker)

            # todo: prompt to insert value and date for unknown tickers.
            if price_tuple == ('failed', 'call'):
                price_tuple = (parse("2020-11-21").date(), 1)
                meta.update(
                    {"error": "{stock ticker not found, insert manually}"})
            entries.append(
                data.Price(meta, price_tuple[0], ticker, amount.Amount(D(round(price_tuple[1], 2)), "DKK"))
            )

        return entries
