#!/usr/bin/env python3

from beancount.ingest import importer
from beancount.core import flags
from ..CommonImporter import *
from beancount.core.position import Cost, CostSpec


from datetime import date
from dateutil.parser import parse

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
        known_accounts = getAccounts()
        prev_trans_date = date.today()
        cash_holdings_dkk = 0
        seen_dates = []

        with open(f.name, encoding="utf-16-le") as f:
            for _ in range(1):  # first line has headers
                next(f)
            ff = enumerate(csv.reader(f, delimiter='\t'))
            for index, row in reversed(list(ff)):

                trans_date = parse(row[1]).date()
                meta = data.new_metadata(f.name, index)
                trans_type = row[5]
                currency = row[15]
                currency_modifier = stringToDecimalFromDA(row[20])
                cash_delta = stringToDecimalFromDA(row[14])
                result_of_sale = stringToDecimalFromDA(row[17])
                ticker = row[6].split(" ")[0]
                amount_of_shares = stringToDecimalFromDA(row[9])
                cost_per_share = round(stringToDecimalFromDA(row[10]) * currency_modifier, 2)
                total_before_commission = amount_of_shares * cost_per_share
                commission = stringToDecimalFromDA(row[25])
                transaction_text = row[21]
                trans_entity = row[7]
                narration = trans_type + ":" + trans_entity

                if trans_date not in seen_dates:
                    seen_dates.append(trans_date)
                    if trans_type != "INDBETALING":
                        # if we haven't seen this day before
                        entries.append(
                            # have to apply on day before, balance is date dependent and not based on order
                            data.Balance(meta, trans_date,
                                         self.source_account,
                                         # must subtract initial cost to have "before" picture
                                         # might cause issues if there are close dates...we will find out.
                                         amount.Amount(D(cash_holdings_dkk), 'DKK'), None, None))
                cash_holdings_dkk = stringToDecimalFromDA(row[19])

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
                ticker_account = self.source_account.replace("Cash", ticker)

                # make posting buying stock ticker as currency
                if trans_type == "KØBT":

                    openAccountIfMissing(entries, ticker_account, known_accounts, ticker, trans_date, meta)

                    # to avoid unbalanced amounts,self-fulfilling prophecy--what matters is what I paid in sum.

                    txn.postings.append(
                        data.Posting(ticker_account,
                                     amount.Amount(D(amount_of_shares), ticker),
                                     Cost(-1 * round((D(cash_delta) + D(commission)) / D(amount_of_shares), 4),
                                          currency, trans_date, None),
                                     None, None, None)
                    )
                    # minus commission posting
                    appendCommissionPosting(
                        txn,
                        self.commission_account,
                        commission,
                        False,
                        currency
                    )

                    # minus cash it cost
                    txn.postings.append(
                        data.Posting(self.source_account,
                                     amount.Amount(D(cash_delta), currency), None, None, None, None)
                    )
                    entries.append(txn)
                    entries.append(
                        data.Price(meta, trans_date, ticker, amount.Amount(D(cost_per_share), "DKK"))
                    )
                elif trans_type == "SOLGT":
                    # determine original cost based on profit
                    cost_basis = (cash_delta - result_of_sale - commission) / amount_of_shares
                    # make posting buying stock ticker as currency
                    txn.appendStockSellingPosting(
                        ticker, ticker_account, trans_date,
                        amount_of_shares, cost_basis, cost_per_share, currency
                    )
                    txn.postings.append(
                        data.Posting(ticker_account,
                                     amount.Amount(amount_of_shares * -1, ticker),
                                     CostSpec(D(cost_basis), None, currency, None, None, None),
                                     amount.Amount(cost_per_share, currency), None, None)
                    )

                    # cash gained from sale
                    txn.postings.append(
                        data.Posting(self.source_account,
                                     amount.Amount(D(cash_delta), currency),
                                     None, None, None, None)
                    )
                    # minus commission
                    appendCommissionPosting(
                        txn,
                        self.commission_account,
                        commission,
                        False,
                        currency
                    )
                    # net profit
                    txn.postings.append(
                        data.Posting(self.sales_account, None, None, None, None, None)
                    )
                    entries.append(txn)
                elif trans_type == "UDB.":
                    dividend_meta_info = {
                        "calculation": "{" +
                                       str(amount_of_shares) + " " + ticker +
                                       "} @ " +
                                       str(cost_per_share) + " " + currency
                    }
                    # store this for next line--where we apply the gain with the tax line
                    temp_dividend_0 = data.Posting(self.dividends_account,
                                                   amount.Amount(total_before_commission * -1, currency),
                                                   None,
                                                   None,
                                                   None,
                                                   dividend_meta_info)
                    temp_dividend_2 = total_before_commission

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
                        data.Posting(self.source_account,
                                     amount.Amount(temp_dividend_2 + cash_delta, currency),
                                     None, None, None, None)
                    )
                    entries.append(txn)
                # TODO: Cannot figure out how to split/sell on several purchases differing cost basis yet
                # Even the numbers manually provided were wrong (by small rounding errors.)
                elif trans_type == "TODO" and transaction_text.split(" ")[0] == "SPLIT" and "OLD" not in ticker:
                    split_ratio_0 = stringToDecimalFromDA(transaction_text.split(" ")[1].split(":")[0])
                    split_ratio_1 = stringToDecimalFromDA(transaction_text.split(" ")[1].split(":")[1])
                    old_amount_of_shares = amount_of_shares
                    new_amount_of_shares = amount_of_shares * split_ratio_1 / split_ratio_0
                    old_cost = round(cash_delta / old_amount_of_shares, 3)
                    new_cost = round(cash_delta / new_amount_of_shares, 3)
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
