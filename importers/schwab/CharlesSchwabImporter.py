#!/usr/bin/env python3
import sys
import re
from beancount.core.number import D
from beancount.ingest import importer
from beancount.core import amount, account, position
from beancount.core import flags
from beancount.core import data, inventory
from ..CommonImporter import *
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
        if re.search("(Investments_Transactions)", os.path.basename(f.name)):
            return True
        else:
            return False

    def file_name(self, f):
        return 'Charles-Schwab-Investment-Transactions.csv'

    def file_account(self, _):
        return self.source_account.replace(":Depot:Cash", "")

    def extract(self, f):
        entries = []
        known_accounts = getAccounts()

        with open(f.name, encoding="ascii") as f:
            for _ in range(2):  # first 2 lines has headers
                next(f)
            ff = enumerate(csv.reader(f, delimiter=','))
            for index, row in reversed(list(ff)):

                trans_type = row[1]
                trans_date = row[0]
                if "as of" in trans_date:
                    trans_date = trans_date.split("as of")[0]

                trans_date = parse(
                    datetime.datetime.strftime(
                        trans_date,
                        "%m/%d/%Y ")
                ).date()

                # Reinvest Dividend => Reinvest Shares
                # Qual Div Reinvest => Reinvest Shares
                # Long Term Cap Gain Reinvest => Reinvest Shares
                # Bank Interest: handle date different
                # Sell, Buy
                # Journal: internal transfer
                ticker = row[2]
                descriptions = row[3]
                amount_of_shares = D(row[4])  # 0.6297
                commission = row[6]  # should be empty always
                cost_per_share = D(str(row[5]).replace("$", ""))  # $9.7192
                total_incl_commission = D(str(row[7]).replace("$", ""))  # $0.02

                narration = trans_type + ":" + descriptions

        return entries
