import json
import tkinter as tk
import sys


def get_accounts():
    accounts = []
    with open(sys.argv[3]) as f:
        for line in f:
            if "open" in line:
                line = line.split(" ")
                accounts.append(line[2].replace("\n", ""))
    return accounts


def get_categories():
    with open(sys.argv[2]) as f:
        mapping = json.load(f)
        return mapping


def split_acc_types():
    account_mapping = get_accounts()
    expense_mapping = []
    income_mapping = []
    for acct in account_mapping:
        if "Expenses" in acct:
            expense_mapping.append(acct)
        else:
            income_mapping.append(acct)
    return expense_mapping, income_mapping


def setup_window():
    root = tk.Tk()
    root.geometry("400x400")

    return root


def format_window(root, description, cost, date, purchase_mapping, expense_mapping, income_mapping):

    def getInput():
        account = clicked1.get()
        if account == "Expenses":
            account = clicked2.get()
        # nonlocal description
        # description = exceptions(description, account)
        add_category(description, account, purchase_mapping)
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
            return description+" "+date
        else:
            return description


def exceptions(description, account):
    recurring_but_different = get_exceptions()

    for value in recurring_but_different:
        if value in description:
            split_acc = account.split(":")
            periods = len(account.split(":"))
            description = description + ": " + split_acc[periods-1]
            break

    return description


def add_category(description, account, purchase_mapping):

    purchase_mapping[description] = account

    with open(sys.argv[2], 'w') as f:
        json.dump(purchase_mapping, f)

    return purchase_mapping
