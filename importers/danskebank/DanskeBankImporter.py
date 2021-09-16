#!/usr/bin/env python3

from beancount.core.number import D
from beancount.ingest import importer
from beancount.core import account
from beancount.core import amount
from beancount.core import flags
from beancount.core import data
from beancount.core.position import Cost
from ..Classifier import  GetInfo


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
        if os.path.basename(f.name) == "dk-bk.csv":
            return True
        else:
            return False

    def extract(self, f):
        entries = []



        with open(f.name) as f:
            for _ in range(1):  # first 3 lines are garbage
                next(f)

            for index, row in enumerate(csv.reader(f, delimiter=';')):
                trans_date = datetime.datetime.strptime(row[0], "%d.%m.%Y").strftime("%Y-%m-%d")
                trans_date = parse(trans_date).date()
                trans_desc = row[1].replace(")", "")
                trans_amt = float(row[2].replace(".", "").replace(",", "."))
                trans_amt = '{:.2f}'.format(trans_amt)
                trans_amt_dec = D(trans_amt)

                meta = data.new_metadata(f.name, index)

                destination_account = GetInfo(trans_desc, trans_amt_dec)

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
                    data.Posting(destination_account, amount.Amount(D(trans_amt_dec *-1),
                                                             'DKK'), None, None, None, None)
                )
                entries.append(txn)

        return entries