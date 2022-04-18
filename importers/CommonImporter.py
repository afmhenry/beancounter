# might try to make common helper functions here
import re
from decimal import Decimal
import os

import beancount.core.data
import requests
import feedparser
import sys
import json
import datetime
from datetime import date

from beancount.core.position import Cost, CostSpec
from dateutil.parser import parse
from beancount.core.number import D
from beancount.core import data
from beancount.core import amount
import tkinter as tk


def danishToStdDec(value):
    return Decimal(
        value.replace("-", "")
        .replace(".", "")
        .replace(",", ".")
    )


def consumeConfigProvidePostings(pre_txn, line_code_pattern, line, code_mapping):
    result = re.search(line_code_pattern, line)
    if result and result.group() in code_mapping:
        line_config = dict.get(code_mapping, result.group())
        account = line_config[0]
        metadata = None
        meta_contents = []
        trans_date = None
        for i, entry in enumerate(line_config[1]):
            extraction = danishToStdDec(re.findall(entry[0], line)[entry[1]])
            meta_contents.append(extraction)
        if len(line_config[1]) == 2:
            if result.group() == "Overført via NemKonto":
                trans_date = (parse(
                    datetime.datetime.strptime(str(meta_contents[1]), "%d%m%Y")
                    .strftime("%Y-%m-%d")).date()
                )
            else:
                metadata = {
                    "calc":
                        str(meta_contents[0]) + " DKK @ " +
                        str(meta_contents[1]) + "%"
                }
        elif len(line_config[1]) == 3:
            metadata = {
                "calc":
                    "(" + str(meta_contents[0]) + " - " + str(meta_contents[2]) + ") DKK @ " +
                    str(meta_contents[1]) + "%"
            }
        if "Firmabidrag" in account:
            appendPayslipPosting(pre_txn,
                                 account.replace(
                                     "Assets:Investment:", "Income:"),
                                 meta_contents[0], metadata)

        appendPayslipPosting(pre_txn, account, meta_contents[0], metadata)

        return trans_date


def appendPayslipPosting(pre_txn, account, value, metadata):
    if "Income" in account:
        value *= -1
    pre_txn.append(
        data.Posting(
            account,
            amount.Amount(
                value,
                "DKK"),
            None,  # Cost or CostSpec
            None,  # price
            None,  # flag
            metadata  # metadata dict
        )
    )


def appendCommissionPosting(txn, account, commission, commission_is_negative, currency):
    if commission_is_negative:
        commission = D(commission) * -1
    else:
        commission = D(commission)

    if commission:
        txn.postings.append(
            data.Posting(
                account,
                amount.Amount(
                    commission,
                    currency),
                None,  # Cost or CostSpec
                None,  # price
                None,  # flag
                None  # metadata dict
            )
        )


def appendStockPurchasePosting(txn, ticker, account, trans_date, amount_of_shares, share_price, currency):
    # purchase posting

    txn.postings.append(
        data.Posting(
            account,
            amount.Amount(D(amount_of_shares), ticker),
            Cost(D(share_price),
                 currency,
                 trans_date,
                 None),  # label--seems that  I can define lots here...todo: look into that
            None,
            None,  # flag
            None  # metadata dict
        )
    )


def appendStockSellingPosting(txn, ticker, account, trans_date,
                              amount_of_shares, open_share_price, close_share_price, currency):
    txn.postings.append(
        data.Posting(
            account,
            amount.Amount(D(amount_of_shares), ticker),
            CostSpec(
                D(open_share_price),
                None,
                currency,
                trans_date,
                None,
                None),
            amount.Amount(close_share_price, currency),  # price
            None,  # flag
            None  # metadata dict
        )
    )


def openAccountIfMissing(entries, account_name, known_accounts, ticker, trans_date, meta):
    if account_name not in known_accounts:
        entries.append(
            data.Open(
                meta,
                trans_date + datetime.timedelta(days=-1),
                account_name,
                [ticker],
                None
            )
        )
        known_accounts.append(account_name)


def getCurrentStockPrice(ticker):
    # auth is bash env variable...easier this way.
    access_key = os.environ["marketstack_pass"]

    base_url = "http://api.marketstack.com/v1/"
    ticker_path = "tickers"
    ticker_parameters = {'access_key': access_key, "search": ticker}

    options = getAPI(base_url + ticker_path, ticker_parameters)
    for option in options:
        if option["symbol"].split(".")[1] in ["XETRA", "XCSE"]:
            price_url = "eod"
            price_parameters = {'access_key': access_key,
                                "symbols": option["symbol"]}
            prices = getAPI(base_url + price_url, price_parameters)
            close_price = Decimal(prices[0].get("close")) * 1
            close_date = prices[0].get("date")
            # todo: handle errors in this api better.
            # if the ticker is on german bourse, convert to dkk from eur
            if option["symbol"].split(".")[1] == "XETRA":
                close_price *= convertInputCurrToDKK("EUR")
            # can easily re-use logic to convert usd to eur
            # return tuple with date,price
            return formatMarketstackDate(close_date), close_price

    return parse("2020-11-21").date(), -1


def formatMarketstackDate(date_string):
    return parse(datetime.datetime.strptime(date_string.replace("+0000", ""), "%Y-%m-%dT%H:%M:%S")
                 .strftime("%Y-%m-%d")).date()


def convertInputCurrToDKK(currency):
    price_feed = feedparser.parse("https://www.nationalbanken.dk/en/statistics/exchange_rates/Pages/_vti_bin/DN"
                                  "/DataService.svc/CurrencyRateRSS?lang=en&iso=" + currency)
    entry = price_feed.entries[0]
    return Decimal(entry.description.split(" ")[3].replace(",", ".")) / 100


def getAPI(url, params):
    request = requests.get(url, params=params)
    if request.status_code == 200:
        response = request.json()
        return response.get("data")
    else:
        print(request.status_code)
        print(request.json())
        return ""


def postAPI(url, value):
    request = requests.post(url, json={"message": value})


"""     if request.status_code == 200:
        response = request.json()
        return response.get("data")
    else:
        print(request.status_code)
        print(request.json())
        return "" """


def stringToDecimalFromDA(str_num):
    if str_num != '':
        return Decimal(str_num.replace(".", "").replace(",", "."))
    else:
        return Decimal("0")


def getAccounts():
    accounts = []
    with open(sys.argv[3]) as lines:
        for line in lines:
            if " open " in line and "Equity" not in line:
                line = line.split(" ")
                accounts.append(line[2].replace("\n", ""))
    return accounts


def getTickersWithPriceStatusInLast10Days():
    tickers = []
    with open(sys.argv[3]) as lines:
        for line in reversed(lines.readlines()):
            if " price " in line:
                line = line.split(" ")
                if line[0]:
                    last_run = parse(line[0]).date() + \
                        datetime.timedelta(days=+10)
                    if last_run > date.today():
                        tickers.append(line[2])
    return tickers


def fromAccountsGetTickers(known_accounts):
    ticker_list = []
    for active_account in known_accounts:
        if ("SaxoBank" in active_account or
            "Nordnet" in active_account) and \
                ("Cash" not in active_account and
                 "Income" not in active_account and
                 "Dividends" not in active_account):
            ticker_position = len(active_account.split(":"))
            ticker = active_account.split(":")[ticker_position - 1]
            ticker_list.append(ticker)
    return ticker_list


def getCategories():
    with open(sys.argv[2]) as f:
        mapping = json.load(f)
        return mapping


def splitAccountTypes():
    account_mapping = getAccounts()
    expense_mapping = []
    income_mapping = []
    for acct in account_mapping:
        if "Expenses" in acct:
            expense_mapping.append(acct)
        else:
            income_mapping.append(acct)
    return expense_mapping, income_mapping


def setupWindow():
    root = tk.Tk()
    root.geometry("400x400")

    return root


def formatWindow(root, description, cost, date_of_trans, purchase_mapping, expense_mapping, income_mapping):
    def getInput():
        account = clicked1.get()
        if account == "Expenses":
            account = clicked2.get()
        # nonlocal description
        # description = exceptions(description, account)
        addCategoryMapping(description, account, purchase_mapping)
        # black magic to make the dropdowns die.
        for child in root.winfo_children():
            if str(child.__class__.__name__) == "OptionMenu":
                child.destroy()
        root.quit()

    label = tk.Label(name="description", text=description + "\n" + cost + "\n" + str(date_of_trans),
                     foreground="white",
                     background="black",
                     width=20,
                     height=6
                     )
    label.pack()
    clicked1 = tk.StringVar()
    clicked1.set("Expenses")
    drop1 = tk.OptionMenu(root, clicked1, *expense_mapping)
    drop1.pack()

    clicked2 = tk.StringVar()
    clicked2.set("Income")
    drop2 = tk.OptionMenu(root, clicked2, *income_mapping)
    drop2.pack()

    button = tk.Button(root, name="continue", text="Select",
                       command=getInput, width=30)
    button.pack()
    root.mainloop()

    # todo need to make sure this actually is updated...or at least understand how.
    return purchase_mapping, description


def get_exceptions():
    with open(sys.argv[4]) as f:
        mapping = json.load(f)
        return mapping


def ifExceptionModifyDescription(description, date_of_trans):
    exception_list = get_exceptions()
    for value in exception_list:
        if value in description:
            return description + " " + date_of_trans
        else:
            return description


def exceptions(description, account):
    recurring_but_different = get_exceptions()

    for value in recurring_but_different:
        if value in description:
            split_acc = account.split(":")
            periods = len(account.split(":"))
            description = description + ": " + split_acc[periods - 1]
            break

    return description


def addCategoryMapping(description, account, purchase_mapping):
    purchase_mapping[description] = account

    with open(sys.argv[2], 'w') as f:
        json.dump(purchase_mapping, f)

    return purchase_mapping
