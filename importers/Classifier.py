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


def split_acc_types(account_mapping):
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
    root.geometry("200x200")

    return root


def format_window(root, description, cost, date, purchase_mapping, expense_mapping, income_mapping):
    # split map into sections
    account_mapping = expense_mapping
    if float(cost) > 0:
        account_mapping = income_mapping

    def show():
        add_category(description, clicked.get(), purchase_mapping)
        # black magic to make the dropdown die.
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
    clicked = tk.StringVar()
    clicked.set(account_mapping[0])
    drop = tk.OptionMenu(root, clicked, *account_mapping)
    drop.pack()

    button = tk.Button(root, name="continue", text="Select", command=show, width=30)
    button.pack()
    root.mainloop()

    # todo need to make sure this actually is updated...or at least understand how.
    return purchase_mapping


def add_category(description, account, purchase_mapping):

    purchase_mapping[description] = account

    with open(sys.argv[2], 'w') as f:
        json.dump(purchase_mapping, f)

    return purchase_mapping
