#!/usr/bin/env python3
import sys
import re
from openpyxl import Workbook, load_workbook

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
        if re.search("(TradesExecuted_)", os.path.basename(f.name)):
            return True
        else:
            return False

    def file_name(self, f):
        return 'SaxoBank-Transactions.xlsx'

    def file_account(self, _):
        return self.source_account.replace(":Depot:Cash", "").replace(":ASK:Cash", "")

    def extract(self, f):
        entries = []
        known_accounts = get_accounts()
        print(f.name)
        wb = load_workbook(f.name)
        sheet_names = wb.get_sheet_names()
        sheet = wb.get_sheet_by_name(sheet_names[1])
        lookup_sheet = wb.get_sheet_by_name(sheet_names[2])
        lookup_closed_sheet = wb.get_sheet_by_name(sheet_names[3])
        destination_account = self.source_account
        lineno = 0
        commission = "0"
        total_excl_commission = "0"

        for row in sheet.values:
            lineno += 1
            if row[0] == "Trade ID":
                continue
            if "ASK" in row[1]:
                # then trades are for ASK account
                destination_account = self.source_account.replace("Depot", "ASK")
            trade_id = row[0]
            trans_instrument = row[2]
            trans_date = parse(datetime.datetime.strftime(row[3], "%Y-%m-%d %H:%M:%S")).date()
            trans_type = row[4]
            amount_of_shares = row[6]
            cost_per_share = "%.4f" % row[7]
            cost_basis = "0"

            # commission, pnl, etc is not calculable if currency is not dkk
            # so lets do it the hard way, lookup on the sheet with more details.
            # god forgive the n^2
            for lookup_row in lookup_sheet.values:
                if lookup_row[0] == trade_id and lookup_row[8] == "Commission":
                    commission = "%.2f" % lookup_row[10]
                elif lookup_row[0] == trade_id and lookup_row[8] == "Share Amount":
                    total_excl_commission = "%.2f" % lookup_row[10]
                    cost_per_share = "%.4f" % abs(lookup_row[10] / amount_of_shares)

            ticker = row[11].split(":")[0]
            bourse = row[11].split(":")[1]
            fund_type = row[16]
            currency = row[18]
            meta = data.new_metadata(f.name, lineno)
            payee = trans_type + ":" + ticker + ":" + fund_type + ":" + str.upper(bourse)

            txn = data.Transaction(
                meta=meta,
                date=trans_date,
                flag=flags.FLAG_OKAY,
                payee=payee,
                narration=trans_instrument,
                tags=set(),
                links=set(),
                postings=[],
            )

            if trans_type == "Bought":
                directions = createAccountIfMissing(destination_account.replace("Cash", ticker), known_accounts, ticker,
                                                    trans_date, meta)
                if directions[0]:
                    entries.append(directions[1])
                    known_accounts = directions[2]

                txn.postings.append(
                    data.Posting(destination_account.replace("Cash", ticker),
                                 amount.Amount(D(amount_of_shares), ticker),
                                 Cost(D(cost_per_share), currency, trans_date, None),
                                 None, None, None)
                )

                # minus commission
                if commission != 0:
                    txn.postings.append(
                        data.Posting(self.commission_account,
                                     amount.Amount(D(commission) * -1, currency),
                                     None, None, None, None)
                    )
                # minus cash it cost
                txn.postings.append(
                    data.Posting(destination_account,
                                 amount.Amount(D(total_excl_commission) + D(commission), currency), None, None, None,
                                 None)
                )
                entries.append(txn)

            elif trans_type == "Sold":

                # another lookup to appended sheet to get cost basis
                for lookup_row in lookup_closed_sheet.values:
                    if lookup_row[9] == trade_id:
                        cost_basis = "%.2f" % lookup_row[12]
                        cost_per_share = "%.2f" % lookup_row[13]
                        opened_date = parse(datetime.datetime.strftime(lookup_row[1], "%Y-%m-%d %H:%M:%S")).date()


                directions = createAccountIfMissing(destination_account.replace("Cash", ticker),
                                                    known_accounts,
                                                    ticker,
                                                    trans_date,
                                                    meta)
                if directions[0]:
                    entries.append(directions[1])
                    known_accounts = directions[2]

                txn.postings.append(
                    data.Posting(destination_account.replace("Cash", ticker),
                                 amount.Amount(D(amount_of_shares), ticker),
                                 CostSpec(D(cost_basis), None, currency, opened_date, None, None),
                                 amount.Amount(D(cost_per_share), currency), None, None)
                )

                # minus commission
                if commission != 0:
                    txn.postings.append(
                        data.Posting(self.commission_account,
                                     amount.Amount(D(commission) * -1, currency),
                                     None, None, None, None)
                    )
                # minus cash it cost
                txn.postings.append(
                    data.Posting(destination_account,
                                 amount.Amount(D(total_excl_commission) + D(commission), currency), None, None, None,
                                 None)
                )
                entries.append(txn)

            else:
                print()

        return entries
