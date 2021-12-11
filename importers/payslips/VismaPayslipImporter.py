#!/usr/bin/env python3
import sys
import re
import PyPDF2

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
from tika import parser  # pip install tika

import csv
import os
import re


class Importer(importer.ImporterProtocol):
    def __init__(self, income_account, destination_account, tax_account, pension_account, pension_income,
                 other_account):
        self.income_account = income_account
        self.destination_account = destination_account
        self.tax_account = tax_account
        self.pension_account = pension_account
        self.pension_income = pension_income
        self.other_account = other_account

    def identify(self, f):
        if re.search("(Lønseddel)", os.path.basename(f.name)):
            return True
        else:
            return False

    def file_name(self, f):
        return 'Payslip.pdf'

    def file_account(self, _):
        return self.income_account

    def file_date(self, file):
        date_str = re.findall("[0-9]{2}.[0-9]{2}.[0-9]{4}", file.name)[0]
        file_date = datetime.datetime.strptime(date_str, "%d.%m.%Y").strftime("%Y-%m-%d")
        file_date = parse(file_date).date()
        return file_date

    def extract(self, f):
        entries = []

        # extremely hacky parsing--regex may need adjustment if there are new lines, or some values get bigger
        # for example if a number goes from hundreds to thousands, thousands to tens of thousands.
        raw = parser.from_file(f.name)
        all_info = str.split(raw['content'], "Sats       Beløb")[1].split("AM-grundlag")[0]
        lines = str.splitlines(all_info)

        gross_pay = re.findall("[0-9]{2}\.[0-9]{3},[0-9]{2}", lines[1])[0]
        gross_pay = danishToStdDec(gross_pay)
        # print(gross_pay)

        firm_pension_contribution = re.findall("[0-9]\.[0-9]{3},[0-9]{2}", lines[8])[0]
        firm_pension_contribution = danishToStdDec(firm_pension_contribution)
        firm_pension_contribution_percentage = re.findall("[0-9]{2},[0-9]{2}", lines[8])[2]
        firm_pension_contribution_percentage = danishToStdDec(firm_pension_contribution_percentage)
        # print(firm_pension_contribution, firm_pension_contribution_percentage)

        own_pension_contribution = re.findall("[0-9]\.[0-9]{3},[0-9]{2}-", lines[9])[0]
        own_pension_contribution = danishToStdDec(own_pension_contribution)
        own_pension_contribution_percentage = re.findall("[0-9],[0-9]{2}", lines[9])[1]
        own_pension_contribution_percentage = danishToStdDec(own_pension_contribution_percentage)
        # print(own_pension_contribution, own_pension_contribution_percentage)

        atp_sats = re.findall("[0-9]{2},[0-9]{2}-", lines[11])[0]
        atp_sats = danishToStdDec(atp_sats)
        # print(atp_sats)

        am_bidrag = re.findall("[0-9]\.[0-9]{3},[0-9]{2}-", lines[13])[0]
        am_bidrag = danishToStdDec(am_bidrag)
        am_bidrag_base = re.findall("[0-9]{2}\.[0-9]{3},[0-9]{2}", lines[13])[0]
        am_bidrag_base = danishToStdDec(am_bidrag_base)
        am_bidrag_percentage = re.findall("[0-9],[0-9]{2}", lines[13])[1]
        am_bidrag_percentage = danishToStdDec(am_bidrag_percentage)
        # print(am_bidrag, am_bidrag_base, am_bidrag_percentage)

        a_skat = re.findall("[0-9]{2}\.[0-9]{3},[0-9]{2}-", lines[14])[0]
        a_skat = danishToStdDec(a_skat)
        a_skat_base = re.findall("[0-9]{2}\.[0-9]{3},[0-9]{2}", lines[14])[0]
        a_skat_base = danishToStdDec(a_skat_base)
        a_skat_fradrag = re.findall("[0-9]\.[0-9]{3},[0-9]{2}", lines[14])[1]
        a_skat_fradrag = danishToStdDec(a_skat_fradrag)
        a_skat_percentage = re.findall("[0-9]{2},[0-9]{2}", lines[14])[2]
        a_skat_percentage = danishToStdDec(a_skat_percentage)
        # print(a_skat, a_skat_base, a_skat_fradrag, a_skat_percentage)

        frokost_ordning = re.findall(" [0-9]{3},[0-9]{2}-", lines[15])[0]
        frokost_ordning = danishToStdDec(frokost_ordning)
        # print(frokost_ordning)

        net_pay = re.findall("[0-9]{2}\.[0-9]{3},[0-9]{2}", lines[25])[0]
        net_pay = danishToStdDec(net_pay)
        # print(net_pay)
        date_of_deposit = re.findall("[0-9]{2}-[0-9]{2}-[0-9]{4}", lines[25])[0]
        date_of_deposit = datetime.datetime.strptime(date_of_deposit, "%d-%m-%Y").strftime("%Y-%m-%d")
        date_of_deposit = parse(date_of_deposit).date()

        meta = data.new_metadata(f.name, 0)
        txn = data.Transaction(
            meta=meta,
            date=date_of_deposit,
            flag=flags.FLAG_OKAY,
            payee="Payslip",
            narration="Detailed input from official payslip",
            tags=set(),
            links=set(),
            postings=[],
        )
        o_pension_meta = {
            "calc":
                str(gross_pay) + " DKK @ " +
                str(own_pension_contribution_percentage) + "%"
        }
        f_pension_meta = {
            "calc":
                str(gross_pay) + " DKK @ " +
                str(firm_pension_contribution_percentage) + "%"
        }
        am_meta = {
            "calc":
                str(am_bidrag_base) + " DKK @ " +
                str(am_bidrag_percentage) + "%"
        }
        as_meta = {
            "calc":
                "(" + str(a_skat_base) + " - " + str(a_skat_fradrag) + ") DKK @ " +
                str(a_skat_percentage) + "%"
        }
        txn.postings.append(
            data.Posting(self.income_account,
                         amount.Amount(-1 * gross_pay, "DKK"),
                         None, None, None, None)
        )
        txn.postings.append(
            data.Posting(self.pension_income + "Firmabidrag",
                         amount.Amount(-1 * firm_pension_contribution, "DKK"),
                         None, None, None, f_pension_meta)
        )
        txn.postings.append(
            data.Posting(self.pension_account + "Firmabidrag",
                         amount.Amount(firm_pension_contribution, "DKK"),
                         None, None, None, f_pension_meta)
        )
        txn.postings.append(
            data.Posting(self.pension_account + "Egenbidrag",
                         amount.Amount(own_pension_contribution, "DKK"),
                         None, None, None, o_pension_meta)
        )
        txn.postings.append(
            data.Posting(self.tax_account + "ATP",
                         amount.Amount(atp_sats, "DKK"),
                         None, None, None, None)
        )
        txn.postings.append(
            data.Posting(self.tax_account + "AM-bidrag",
                         amount.Amount(am_bidrag, "DKK"),
                         None, None, None, am_meta)
        )
        txn.postings.append(
            data.Posting(self.tax_account + "A-skat",
                         amount.Amount(a_skat, "DKK"),
                         None, None, None, as_meta)
        )
        txn.postings.append(
            data.Posting(self.other_account,
                         amount.Amount(frokost_ordning, "DKK"),
                         None, None, None, None)
        )
        txn.postings.append(
            data.Posting(self.destination_account,
                         amount.Amount(net_pay, "DKK"),
                         None, None, None, None)
        )

        entries.append(txn)
        return entries
