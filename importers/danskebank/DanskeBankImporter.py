#!/usr/bin/env python3
import sys
import re
from beancount.core.number import D
from beancount.ingest import importer
from beancount.core import account
from beancount.core import amount
from beancount.core import flags
from beancount.core import data
from beancount.core.position import Cost
from ..Classifier import *

from datetime import date
from dateutil.parser import parse
import datetime

from titlecase import titlecase

import csv
import os
import re


class Importer(importer.ImporterProtocol):
    def __init__(self, source_account):
        self.source_account = source_account

    def identify(self, f):
        # Main--20211010
        # (Main)[-][0-9]{10}[-][0-9]{8}
        if re.search("(Main)[-][0-9]{10}[-][0-9]{8}", os.path.basename(f.name)):
            if date.today().strftime("%Y%m%d") in os.path.basename(f.name):
                return True
        else:
            return False

    def extract(self, f):
        entries = []
        accounts = get_accounts()
        account_by_type = split_acc_types(accounts)

        mapping = get_categories()
        root = setup_window()

        with open(f.name, encoding="latin1") as f:
            for _ in range(1):  # first line has headers
                next(f)
            for index, row in enumerate(csv.reader(f, delimiter=';')):
                if "Udført" in row[4]:
                    trans_date = datetime.datetime.strptime(row[0], "%d.%m.%Y").strftime("%Y-%m-%d")
                    trans_date = parse(trans_date).date()
                    trans_desc = row[1]
                    trans_amt = float(row[2].replace(".", "").replace(",", "."))
                    trans_amt = '{:.2f}'.format(trans_amt)
                    trans_amt_dec = D(trans_amt)
                    balance_amt = float(row[3].replace(".", "").replace(",", "."))
                    balance_amt = '{:.2f}'.format(balance_amt)
                    balance_amt_dec = D(balance_amt)

                    meta = data.new_metadata(f.name, index)

                    # todo: create mapping in elegant way--so I can also map new things quickly
                    if trans_desc not in mapping:
                        mapping = format_window(root, trans_desc, trans_amt, trans_date, mapping, account_by_type[0],
                                                account_by_type[1])

                    destination_account = mapping[trans_desc]

                    txn = data.Transaction(
                        meta=meta,
                        date=trans_date,
                        flag=flags.FLAG_OKAY,
                        payee=trans_desc,
                        narration="",
                        tags=set(),
                        links=set(),
                        postings=[],
                    )

                    txn.postings.append(
                        data.Posting(self.source_account, amount.Amount(D(trans_amt),
                                                                        'DKK'), None, None, None, None)
                    )
                    txn.postings.append(
                        data.Posting(destination_account, amount.Amount(D(trans_amt_dec * -1),
                                                                        'DKK'), None, None, None, None)
                    )
                    if index == 2:
                        balance = float(row[3].replace(".", "").replace(",", "."))
                        # txn.postings.append(data.Balance(meta, trans_date, self.source_account, amount.Amount(D(
                        # balance), 'DKK'), None, None))

                    entries.append(txn)
                else:
                    print("Pending purchases")
            if index:
                entries.append(
                    data.Balance(meta, trans_date,
                                 self.source_account,
                                 amount.Amount(balance_amt_dec, 'DKK'), None, None))
        return entries
