from openpyxl import Workbook, load_workbook

from beancount.ingest import importer
from beancount.core import flags
from ..CommonImporter import *
from beancount.core.position import Cost, CostSpec

from dateutil.parser import parse
import datetime

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
        return "documents/" + self.source_account.replace(":Depot:Cash", "").replace(":ASK:Cash", "")

    def extract(self, f):
        entries = []
        known_accounts = getAccounts()
        wb = load_workbook(f.name)
        sheet_names = wb.get_sheet_names()
        sheet = wb.get_sheet_by_name(sheet_names[1])

        # I have merged multiple excel files to a single one--with multiple sheets.
        lookup_sheet = wb.get_sheet_by_name(sheet_names[2])
        lookup_closed_sheet = wb.get_sheet_by_name(sheet_names[3])
        lookup_account_sheet_ASK = wb.get_sheet_by_name(sheet_names[4])
        lookup_account_sheet_Depot = wb.get_sheet_by_name(sheet_names[5])
        destination_account = self.source_account
        lineno = 0
        commission = "0"
        total_excl_commission = "0"
        currency = "DKK"

        for row in sheet.values:
            lineno += 1
            if row[0] == "Trade ID":
                continue
            if "ASK" in row[1]:
                # then trades are for ASK account, not depot
                destination_account = self.source_account.replace("Depot", "ASK")
            trade_id = row[0]
            trans_instrument = row[2]
            trans_date = parse(
                datetime.datetime.strftime(
                    row[3],
                    "%Y-%m-%d %H:%M:%S")
            ).date()
            trans_type = row[4]
            amount_of_shares = row[6]
            close_share_price = "0"
            open_share_price = "0"
            total_incl_commission = "%.2f" % row[10]

            # commission, pnl, etc is not calculable if currency is not dkk
            # so lets do it the hard way, lookup on the sheet with more details.
            # god forgive the n^2
            for lookup_row in lookup_sheet.values:
                if lookup_row[0] == trade_id and lookup_row[8] == "Commission":
                    commission = "%.2f" % lookup_row[10]
                elif lookup_row[0] == trade_id and lookup_row[8] == "Share Amount":
                    total_excl_commission = lookup_row[11]
                    close_share_price = "%.2f" % abs(total_excl_commission / amount_of_shares)

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
            ticker_account = destination_account.replace("Cash", ticker)

            if trans_type == "Bought":
                openAccountIfMissing(
                    entries, ticker_account, known_accounts, ticker, trans_date, meta)

                # purchase posting
                appendStockPurchasePosting(
                    txn,
                    ticker,
                    ticker_account,
                    trans_date,
                    amount_of_shares,
                    close_share_price,
                    currency
                )

                # minus commission posting
                appendCommissionPosting(
                    txn,
                    self.commission_account,
                    commission,
                    True,
                    currency
                )

                # minus cash it cost
                # cash out--i leave it empty due to tiny rounding issues
                purchase_meta_info = {
                    "total_cost": "{" +
                                  str(amount_of_shares) + " " + ticker +
                                  "} @ " +
                                  str(close_share_price) + " = " + total_incl_commission + " " + currency
                }
                txn.postings.append(
                    data.Posting(
                        destination_account,
                        None, None, None, None, purchase_meta_info)
                )
                entries.append(txn)
                entries.append(
                    data.Price(meta, trans_date, ticker, amount.Amount(D(close_share_price), "DKK"))
                )

            elif trans_type == "Sold":

                # another lookup to appended sheet to get cost basis
                for lookup_row in lookup_closed_sheet.values:
                    if lookup_row[9] == trade_id:
                        open_share_price = "%.2f" % lookup_row[12]
                        close_share_price = "%.2f" % lookup_row[13]
                        opened_date = parse(datetime.datetime.strftime(lookup_row[1], "%Y-%m-%d %H:%M:%S")).date()

                openAccountIfMissing(
                    entries, ticker_account, known_accounts, ticker, trans_date, meta)

                # Sell Stock Posting
                txn.postings.append(
                    data.Posting(
                        destination_account.replace("Cash", ticker),
                        amount.Amount(D(amount_of_shares), ticker),
                        CostSpec(D(open_share_price), None, currency, opened_date, None, None),
                        amount.Amount(D(close_share_price), currency), None, None)
                )

                # minus commission posting
                appendCommissionPosting(
                    txn,
                    self.commission_account,
                    commission,
                    True,
                    currency
                )

                # minus cash it cost
                txn.postings.append(
                    data.Posting(
                        destination_account,
                        amount.Amount(D(total_excl_commission) + D(commission), currency), None, None, None,
                        None)
                )
                # profit
                txn.postings.append(
                    data.Posting(
                        self.sales_account,
                        amount.Amount(((D(close_share_price) * D(amount_of_shares)) - (
                            (D(open_share_price) * D(amount_of_shares)))), currency),
                        None, None, None, None)
                )
                entries.append(txn)

            else:
                print()

        # before we return--do lookup for balance transaction for ASK.
        # can eventually do the same for depot...not sure if it should be in the same importer though.

        for i, lookup_row in enumerate(lookup_account_sheet_ASK.values):
            if lookup_row[1] != "Posting Date" and i == 1:
                meta = data.new_metadata("account_balance", 1)
                balance_date = parse(datetime.datetime.strftime(lookup_row[2], "%Y-%m-%d %H:%M:%S")).date()
                balance_amount = lookup_row[5]
                entries.append(
                    data.Balance(
                        meta,
                        balance_date + datetime.timedelta(days=1),
                        self.source_account.replace("Depot", "ASK"),
                        amount.Amount(D("%.2f" % balance_amount), 'DKK'),
                        D(5),
                        None
                    )
                )
            if "Corporate Action" in lookup_row[3]:
                desc = lookup_row[3].split(" ")[1]
                div_date = parse(datetime.datetime.strftime(lookup_row[2], "%Y-%m-%d %H:%M:%S")).date()
                meta = data.new_metadata("AccStatement", 1)

                div_amount = D("%.2f" % lookup_row[4])
                txn = data.Transaction(
                    meta=meta,
                    date=div_date,
                    flag=flags.FLAG_OKAY,
                    payee=desc,
                    narration=lookup_row[3],
                    tags=set(),
                    links=set(),
                    postings=[],
                )
                txn.postings.append(
                    data.Posting(self.dividends_account,
                                 amount.Amount(div_amount * -1, currency),
                                 None, None, None, None)
                )
                txn.postings.append(
                    data.Posting(self.source_account.replace("Depot", "ASK"),
                                 amount.Amount(div_amount, currency),
                                 None, None, None, None)
                )
                entries.append(txn)
        for lookup_row in lookup_account_sheet_Depot.values:
            if lookup_row[1] != "Posting Date":
                meta = data.new_metadata("account_balance", 1)
                balance_date = parse(datetime.datetime.strftime(lookup_row[2], "%Y-%m-%d %H:%M:%S")).date()
                balance_amount = lookup_row[5]
                entries.append(
                    data.Balance(
                        meta,
                        balance_date + datetime.timedelta(days=1),
                        self.source_account,
                        amount.Amount(D("%.2f" % balance_amount), 'DKK'),
                        D(5),
                        None
                    )
                )
                break

        return entries
