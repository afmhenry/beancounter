#!/usr/bin/env python3
import sys
import re
from beancount.core.number import D
from beancount.ingest import importer
from beancount.core import amount
from beancount.core import flags
from beancount.core import data
from ..Classifier import *
from ..CommonImporter import *
from beancount.core.position import Cost

from datetime import date
from dateutil.parser import parse
import datetime

from titlecase import titlecase

import csv
import os
import re


class Importer(importer.ImporterProtocol):
    def __init__(self, account):
        self.account = account

    def identify(self, f):
        if re.search("(transactions-and-notes-export)", os.path.basename(f.name)):
            return True
        else:
            return False

    def extract(self, f):
        entries = []

        with open(f.name, encoding="utf-16-le") as f:
            for _ in range(1):  # first line has headers
                next(f)
            for index, row in enumerate(csv.reader(f, delimiter='\t')):
                trans_date = parse(row[2]).date()
                trans_type = row[5]
                currency = row[15]
                currency_modifier = stringToFloat(row[20])
                cash_delta = stringToFloatString(row[14])
                ticker = row[6]
                share_amount = float(row[9])
                cost_per_share = stringToFloatString(row[10])
                total_before_commission = floatToString(-1 * currency_modifier * share_amount * float(cost_per_share))
                commission = stringToFloatString(row[25])
                transaction_text = row[21]
                trans_entity = row[7]
                meta = data.new_metadata(f.name, index)
                narration = trans_type + ":"+trans_entity

                if transaction_text != "":
                    narration += ":"+transaction_text

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
                if trans_type == 'KØBT':
                    # make posting buying stock ticker as currency
                    destination_account = self.account.replace("Cash", ticker)
                    txn.postings.append(
                        data.Posting(destination_account, amount.Amount(D(share_amount),
                                                                        ticker), Cost(D(cost_per_share),
                                                                                      currency, trans_date, None), None,
                                     None, None)
                    )
                    # minus cash it cost
                    txn.postings.append(
                        data.Posting(self.account, amount.Amount(D(total_before_commission),
                                                                 currency), None, None, None, None)
                    )
                    # minus commission
                    if float(commission) > 0:
                        txn.postings.append(
                            data.Posting("Expenses:Trading:Commissions", amount.Amount(D(commission) * -1,
                                                                                       currency), None, None, None,
                                         None)
                        )
                elif trans_type == "":
                    # SOLGT,UDBYTTESKAT, UDB. to be handled
                    print()
                entries.append(txn)

            #somehow apply balance

                # date format: 2021-10-15
                # currency format: 1.447,32

                ##file has columns
                # 0: Id: unique id for transaction
                # 1: bogføringsdag: the day stock begin transfer
            # 2: Handelsdag: day of actual purchase
            # 3: Valørdag: day of transfer ownership
            # 4: Depot
            # 5: Transaction Type
            # UDBYTTESKAT
            # UDB.
            # KØBT
            # INDBETALING
            # SOLGT
            # blank (splitStock splits are currently dealt with by emptying an account’s positions and recreating the positions at a different price:
            # 6: Værdipapirer: The stock ticker
            # 7: Værdipapirtype: description of entity
            # 8: ISIN: International Securities Identification Number (ISIN) is a 12-digit alphanumeric code that uniquely identifies a specific security.
            # 9: Antal: Amount
            # 10: Kurs: the cost of entity
            # Kurs*Antal*vekslingskurs
            # 11: Rente: Interest or taxes deducted
            # 12: samlede afgifter: total expense of trade
            # 13: samlede afgifter valuta: currency of total expense of trade
            # 14: beløb: money used on trade for that instrument
            # 15: valuta: currency
            # 16: indkøbsværdi: purchase value in native currency
            # indkøbsværdi * vekslingskurs = total amount traded in ticker
            # 17: resultat: realized gains or losses
            # 18: total antal: amount of stocks held
            # 19: saldo: amount in account--balance maybe?
            # 20: vekslingskurs: conversion rate
            # 21: transaktiontekst: description
            # 25: kurtage: cost, null if not relevant,
            # 26: kurtage valuta: currency
            # open account if new ticker introduced

        return entries
