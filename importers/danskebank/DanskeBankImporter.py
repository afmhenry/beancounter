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
from ..CommonImporter import *

from titlecase import titlecase

import csv
import os
import re


class Importer(importer.ImporterProtocol):
    def __init__(self, account):
        self.account = account

    def identify(self, f):
        if re.search("(Main)[-][0-9]{10}[-][0-9]{8}", os.path.basename(f.name)):
            # if date.today().strftime("%Y%m%d") in os.path.basename(f.name):
            return True
        else:
            return False

    def file_name(self, f):
        return 'Danske-Bank-Checking.csv'

    def file_account(self, _):
        return "documents/"+self.account

    def extract(self, f):
        entries = []
        account_by_type = splitAccountTypes()

        mapping = getCategories()
        root = setupWindow()
        trans_date = date.today()
        with open(f.name, encoding="iso-8859-1") as f:
            for _ in range(1):  # first line has headers
                next(f)
            for index, row in enumerate(csv.reader(f, delimiter=';')):
                # the fools at Danskbank made a breaking change on the file, so I have to offset....
                i = 2
                if "Udført" in row[4+i]:
                    trans_date = datetime.datetime.strptime(row[0], "%d.%m.%Y").strftime("%Y-%m-%d")
                    trans_date = parse(trans_date).date()
                    trans_desc = row[1+i]
                    trans_amt = float(row[2+i].replace(".", "").replace(",", "."))
                    trans_amt = '{:.2f}'.format(trans_amt)
                    trans_amt_dec = D(trans_amt)
                    balance_amt = float(row[3+i].replace(".", "").replace(",", "."))
                    balance_amt = '{:.2f}'.format(balance_amt)
                    balance_amt_dec = D(balance_amt)

                    meta = data.new_metadata(f.name, index)

                    # This would be a repeat since we read in payslip separately.
                    # The posting will show up there with a lot more info
                    #if "Lønoverførsel" == trans_desc:
                        #continue
                    trans_desc = ifExceptionModifyDescription(trans_desc, trans_date.strftime("%d-%m-%Y"))
                    if trans_desc in mapping:
                        destination_account = mapping[trans_desc]
                    else:
                        mappings = formatWindow(root, trans_desc, trans_amt, trans_date, mapping, account_by_type[0],
                                                account_by_type[1])
                        destination_account = mappings[0][mappings[1]]
                        mapping = mappings[0]

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
                        data.Posting(self.account,
                                     amount.Amount(D(trans_amt), 'DKK'),
                                     None, None, None, None)
                    )
                    txn.postings.append(
                        data.Posting(destination_account,
                                     amount.Amount(D(trans_amt_dec * -1), 'DKK'),
                                     None, None, None, None)
                    )

                    # at start of file balance
                    if index == 0:
                        entries.append(
                            # have to apply on day before, balance is date dependent and not based on order
                            data.Balance(meta, trans_date + datetime.timedelta(days=-1),
                                         self.account,
                                         # must subtract initial cost to have "before" picture
                                         # might cause issues if there are close dates...we will find out.
                                         amount.Amount(balance_amt_dec + trans_amt_dec * -1, 'DKK'), None, None))
                    entries.append(txn)

                # else pending purchases, will get them next file when they are ready.

            # At end of file, balance
            meta = data.new_metadata(f.name, index)
            entries.append(
                data.Balance(meta, trans_date + datetime.timedelta(days=1),
                             self.account,
                             amount.Amount(balance_amt_dec, 'DKK'), None, None))
        return entries
