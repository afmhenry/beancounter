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
                currency_modifier = stringToDecimal(row[20])
                cash_delta = stringToDecimal(row[14])
                result_of_sale = stringToDecimal(row[17])
                cash_holdings_dkk = stringToDecimal(row[19])
                ticker = row[6].split(" ")[0]
                amount_of_shares = stringToDecimal(row[9])
                cost_per_share = round(stringToDecimal(row[10]) * currency_modifier, 2)
                total_before_commission = round(amount_of_shares * cost_per_share, 2)
                commission = stringToDecimal(row[25])
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
                    if destination_account not in known_accounts:
                        # function to create
                        entries.append(
                            data.Open(meta,
                                      trans_date + datetime.timedelta(days=-1),
                                      destination_account,
                                      [ticker],
                                      None
                                      )
                        )
                        known_accounts.append(destination_account)
                    inventory.Position(amount.Amount(D(amount_of_shares), ticker),
                                       Cost(D(cost_per_share), currency, trans_date, None))
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
                                     None, None, None, None, None)
                    )
                    entries.append(txn)
                elif trans_type == "SOLGT":
                    # determine original cost based on profit
                    cost_basis = round((cash_delta - result_of_sale - commission) / amount_of_shares, 2)
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
                                     amount.Amount(D(total_before_commission), currency),
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
                        data.Posting(self.sales_account, None,
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
                    temp_dividend_0 = data.Posting(self.dividends_account,
                                                   amount.Amount(total_before_commission * -1, currency),
                                                   None,
                                                   None,
                                                   None,
                                                   dividend_meta_info)
                    temp_dividend_2 = data.Posting(self.source_account, None,
                                                   None, None, None, None)

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
                        temp_dividend_2
                    )
                    entries.append(txn)

                elif trans_type == "ewew" and transaction_text.split(" ")[0] == "SPLIT" and "OLD" not in ticker:
                    split_ratio_0 = stringToDecimal(transaction_text.split(" ")[1].split(":")[0])
                    split_ratio_1 = stringToDecimal(transaction_text.split(" ")[1].split(":")[1])
                    old_amount_of_shares = amount_of_shares
                    new_amount_of_shares = amount_of_shares * split_ratio_1 / split_ratio_0
                    old_cost = round(cash_delta / old_amount_of_shares, 2)
                    new_cost = round(cash_delta / new_amount_of_shares, 2)
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
