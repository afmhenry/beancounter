# might try to make common helper functions here
from decimal import Decimal
import xlrd
import csv
import os
import requests
import sys
import json
import datetime
from beancount.core import data
import tkinter as tk


def getCurrentStockPrice(ticker):
    access_key = os.environ["marketstack_pass"]

    base_url = "http://api.marketstack.com/v1/"
    ticker_path = "tickers"
    ticker_parameters = {'access_key': access_key, "search": ticker}

    options = json.loads(getAPI(base_url + ticker_path, ticker_parameters))
    for option in options:
        if option["symbol"].split(".")[1] in ["XETRA", "XCSE"]:
            price_url = "eod"
            price_parameters = {'access_key': access_key, "symbols": option["symbol"]}
            prices = json.load(getAPI(price_url, price_parameters))
            close_price = prices[0]["close"]
            close_date = prices[0]["date"]
            return close_date, close_price

    return "failed", "call"


def getAPI(url, params):
    request = requests.get(url, params=params)
    if request.status_code == 200:
        response = request.json()
        return response.get("data")
    else:
        return ""


def createAccountIfMissing(account_name, known_accounts, ticker, trans_date, meta):
    if account_name not in known_accounts:
        data_obj = data.Open(meta,
                             trans_date + datetime.timedelta(days=-1),
                             account_name,
                             [ticker],
                             None
                             )

        known_accounts.append(account_name)
        return True, data_obj, known_accounts
    else:
        return False, None, None


def stringToDecimalFromDA(str_num):
    if str_num != '':
        return Decimal(str_num.replace(".", "").replace(",", "."))
    else:
        return Decimal("0")


def getAccounts():
    accounts = []
    with open(sys.argv[3]) as f:
        for line in f:
            if " open " in line and "Equity" not in line:
                line = line.split(" ")
                accounts.append(line[2].replace("\n", ""))
    return accounts


def getCategories():
    with open(sys.argv[2]) as f:
        mapping = json.load(f)
        return mapping


def split_acc_types():
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


def formatWindow(root, description, cost, date, purchase_mapping, expense_mapping, income_mapping):
    def getInput():
        account = clicked1.get()
        if account == "Expenses":
            account = clicked2.get()
        # nonlocal description
        # description = exceptions(description, account)
        add_category_mapping(description, account, purchase_mapping)
        # black magic to make the dropdowns die.
        for child in root.winfo_children():
            if str(child.__class__.__name__) == "OptionMenu":
                child.destroy()
        root.quit()

    label = tk.Label(name="description", text=description + "\n" + cost + "\n" + str(date),
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

    button = tk.Button(root, name="continue", text="Select", command=getInput, width=30)
    button.pack()
    root.mainloop()

    # todo need to make sure this actually is updated...or at least understand how.
    return purchase_mapping, description


def get_exceptions():
    with open(sys.argv[4]) as f:
        mapping = json.load(f)
        return mapping


def modify_if_in_exceptions(description, date):
    exception_list = get_exceptions()
    for value in exception_list:
        if value in description:
            return description + " " + date
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


def add_category_mapping(description, account, purchase_mapping):
    purchase_mapping[description] = account

    with open(sys.argv[2], 'w') as f:
        json.dump(purchase_mapping, f)

    return purchase_mapping
