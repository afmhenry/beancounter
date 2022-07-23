from beancount.ingest import importer
from beancount.core import flags
from ..CommonImporter import *

from datetime import date
from dateutil.parser import parse
import datetime

from tika import parser

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
        file_date = datetime.datetime.strptime(
            date_str, "%d.%m.%Y").strftime("%Y-%m-%d")
        file_date = parse(file_date).date()
        return file_date

    def extract(self, f):
        entries = []

        # extremely hacky parsing--regex may need adjustment if there are new lines, or some values get bigger
        # for example if a number goes from hundreds to thousands, thousands to tens of thousands.
        raw = parser.from_file(f.name)
        description = str.split(raw["content"], "Lønseddel for perioden")[
            1].split("\n")[0]
        all_info = str.split(raw['content'], "Sats       Beløb")[
            1].split("AM-grundlag")[0]
        lines = str.splitlines(all_info)
        line_code_pattern = "([0-9]{4,5})|(Overført via NemKonto){1}"

        ##key, account, regexX, positionX
        code_mapping = {
            "1000": (self.income_account, {
                ("[0-9]{2}\.[0-9]{3},[0-9]{2}", 0)}),
            "4621": (self.income_account.replace("GrossSalary", "VacationPay"), {
                ("[0-9]*\.*[0-9]{3},[0-9]{2}", 0)}),
            "4623": (self.income_account.replace("GrossSalary", "VacationBonusPay"), {
                ("[0-9]+\.[0-9]{3},[0-9]{2}", 0)}),
            "6020": (self.pension_account + "Firmabidrag", [
                ("[0-9]\.[0-9]{3},[0-9]{2}", 0),
                ("[0-9]{2},[0-9]{2}", 2)]),
            "6021": (self.pension_account + "Egenbidrag", [
                ("[0-9]\.[0-9]{3},[0-9]{2}-", 0),
                ("[0-9]{1},[0-9]{2}", 1)]),
            "8100": (self.tax_account + "ATP", {
                ("[0-9]{2},[0-9]{2}-", 0)}),
            "8220": (self.tax_account + "AM-bidrag", [
                ("[0-9]\.[0-9]{3},[0-9]{2}-", 0),
                ("[0-9],[0-9]{2}", 1),
                ("[0-9]{2}\.[0-9]{3},[0-9]{2}", 0)]),
            "8250": (self.tax_account + "A-skat", [
                ("[0-9]{2}\.[0-9]{3},[0-9]{2}-", 0),
                ("[0-9]{2},[0-9]{2}", 2),
                ("[0-9]{2}\.[0-9]{3},[0-9]{2}", 0),
                ("[0-9]\.[0-9]{3},[0-9]{2}", 1)]),
            "9501": (self.other_account, {
                ("[0-9]{3},[0-9]{2}-", 0)}),
            "Overført via NemKonto": (self.destination_account, [
                ("[0-9]{2}\.[0-9]{3},[0-9]{2}", 0),
                ("[0-9]{2}-[0-9]{2}-[0-9]{4}", 0)
            ])
        }
        meta = data.new_metadata(f.name, 0)
        pre_txn = []
        trans_date = None
        for line in lines:
            result = consumeConfigProvidePostings(
                pre_txn, line_code_pattern, line, code_mapping)
            if result:
                trans_date = result
        txn = data.Transaction(
            meta=meta,
            date=trans_date,
            flag=flags.FLAG_OKAY,
            payee="Payslip",
            narration="Lønseddel for perioden"+description,
            tags=set(),
            links=set(),
            postings=pre_txn,
        )
        entries.append(txn)

        return entries
