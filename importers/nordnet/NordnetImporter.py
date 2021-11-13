#!/usr/bin/env python3
import sys
import re
from beancount.core.number import D
from beancount.ingest import importer
from beancount.core import amount, account, position
from beancount.core import flags
from beancount.core import data, inventory
from ..CommonImporter import *
from ..Classifier import *
from beancount.core.position import Cost, CostSpec

from beancount.query.query import *

from datetime import date
from dateutil.parser import parse
import datetime

from titlecase import titlecase

import csv
import os
import re


class Importer(importer.ImporterProtocol):
    def __init__(self, source_account, commission_account, sales_account, dividends_account, tax_account):
        self.source_account = source_account
        self.commission_account = commission_account
        self.sales_account = sales_account
        self.dividends_account = dividends_account
        self.tax_account = tax_account

    def identify(self, f):
        if re.search("(transactions-and-notes-export)", os.path.basename(f.name)):
            return True
        else:
            return False

    def file_name(self, f):
        return 'Nordnet-Depot-Transactions.csv'

    def file_account(self, _):
        return self.source_account.replace(":Depot:Cash", "")

    def extract(self, f):
        entries = []
        known_accounts = get_accounts()

        with open(f.name, encoding="utf-16-le") as f:
            for _ in range(1):  # first line has headers
                next(f)
            ff = enumerate(csv.reader(f, delimiter='\t'))
            for index, row in reversed(list(ff)):
                trans_date = parse(row[2]).date()
                trans_type = row[5]
                currency = row[15]
                currency_modifier = stringToDecimalFromDA(row[20])
                cash_delta = stringToDecimalFromDA(row[14])
                result_of_sale = stringToDecimalFromDA(row[17])
                cash_holdings_dkk = stringToDecimalFromDA(row[19])
                ticker = row[6].split(" ")[0]
                amount_of_shares = stringToDecimalFromDA(row[9])
                cost_per_share = round(stringToDecimalFromDA(row[10]) * currency_modifier, 2)
                total_before_commission = amount_of_shares * cost_per_share
                commission = stringToDecimalFromDA(row[25])
                transaction_text = row[21]
                trans_entity = row[7]
                meta = data.new_metadata(f.name, index)
                narration = trans_type + ":" + trans_entity

                if transaction_text != "":
                    narration = transaction_text

                txn = data.Transaction(
                    meta=meta,
                    date=trans_date,
                    flag=flags.FLAG_OKAY,
                    payee=trans_type + "-" + ticker,
                    narration=narration,
                    tags=set(),
                    links=set(),
                    postings=[],
                )

                if trans_type == "KØBT":
                    # make posting buying stock ticker as currency
                    destination_account = self.source_account.replace("Cash", ticker)
                    directions = createAccountIfMissing(destination_account, known_accounts, ticker, trans_date, meta)
                    if directions[0]:
                        entries.append(directions[1])
                        known_accounts = directions[2]

                    txn.postings.append(
                        data.Posting(destination_account,
                                     amount.Amount(D(amount_of_shares), ticker),
                                     Cost(D(cost_per_share), currency, trans_date, None),
                                     None, None, None)
                    )

                    # minus commission
                    if commission > 0:
                        txn.postings.append(
                            data.Posting(self.commission_account,
                                         amount.Amount(D(commission), currency),
                                         None, None, None, None)
                        )
                    # minus cash it cost
                    txn.postings.append(
                        data.Posting(self.source_account,
                                     amount.Amount(D(cash_delta), currency), None, None, None, None)
                    )
                    entries.append(txn)
                elif trans_type == "SOLGT":
                    # determine original cost based on profit
                    cost_basis = (cash_delta - result_of_sale - commission) / amount_of_shares
                    # make posting buying stock ticker as currency
                    destination_account = self.source_account.replace("Cash", ticker)
                    txn.postings.append(
                        data.Posting(destination_account,
                                     amount.Amount(amount_of_shares * -1, ticker),
                                     CostSpec(D(cost_basis), None, currency, None, None, None),
                                     amount.Amount(cost_per_share, currency), None, None)
                    )

                    # cash gained from sale
                    txn.postings.append(
                        data.Posting(self.source_account,
                                     amount.Amount(D(cash_delta)-D(commission), currency),
                                     None, None, None, None)
                    )
                    # minus commission
                    if commission > 0:
                        txn.postings.append(
                            data.Posting(self.commission_account,
                                         amount.Amount(D(commission), currency),
                                         None, None, None, None)
                        )
                    # net profit
                    txn.postings.append(
                        data.Posting(self.sales_account,
                                     amount.Amount(-1*(D(cash_delta)-D(cash_delta - result_of_sale - commission)), currency),
                                     None, None, None, None)
                    )
                    entries.append(txn)
                elif trans_type == "UDB.":
                    dividend_meta_info = {
                        "calculation": "{" +
                                       str(amount_of_shares) + " " + ticker +
                                       "} @ " +
                                       str(cost_per_share) + " " + currency
                    }
                    # store this for next line--where we apply the gain with the tax line
                    temp_dividend_0 = data.Posting(self.dividends_account,
                                                   amount.Amount(total_before_commission * -1, currency),
                                                   None,
                                                   None,
                                                   None,
                                                   dividend_meta_info)
                    temp_dividend_2 = total_before_commission

                elif trans_type == "UDBYTTESKAT":
                    txn.postings.append(
                        temp_dividend_0
                    )
                    txn.postings.append(
                        data.Posting(self.tax_account,
                                     amount.Amount(cash_delta * -1, currency),
                                     None, None, None, None)
                    )
                    txn.postings.append(
                        data.Posting(self.source_account,
                                     amount.Amount(temp_dividend_2 + cash_delta, currency),
                                     None, None, None, None)
                    )
                    entries.append(txn)
                # TODO: Cannot figure out how to split/sell on several purchases differing cost basis yet
                # Even the numbers manually provided were wrong (by small rounding errors.)
                elif trans_type == "TODO" and transaction_text.split(" ")[0] == "SPLIT" and "OLD" not in ticker:
                    split_ratio_0 = stringToDecimalFromDA(transaction_text.split(" ")[1].split(":")[0])
                    split_ratio_1 = stringToDecimalFromDA(transaction_text.split(" ")[1].split(":")[1])
                    old_amount_of_shares = amount_of_shares
                    new_amount_of_shares = amount_of_shares * split_ratio_1 / split_ratio_0
                    old_cost = round(cash_delta / old_amount_of_shares, 3)
                    new_cost = round(cash_delta / new_amount_of_shares, 3)
                    txn.postings.append(
                        data.Posting(self.source_account.replace("Cash", ticker),
                                     amount.Amount(D(new_amount_of_shares * -1), ticker),
                                     CostSpec(D(new_cost), None, currency, None, None, None),
                                     None, None, None)
                    )
                    txn.postings.append(
                        data.Posting(self.source_account.replace("Cash", ticker),
                                     amount.Amount(D(old_amount_of_shares), ticker),
                                     CostSpec(D(old_cost), None, currency, None, None, None),
                                     None, None, None)
                    )
                    entries.append(txn)
        return entries
