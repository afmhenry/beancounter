import json


def get_accounts():
    accounts = []
    with open('accounts.beancount') as f:
        for line in f:
            if "open" in line:
                line = line.split(" ")
                accounts.append(line[2].replace("\n", ""))
    return accounts


def get_category():
    with open('mapping.json') as f:
        mapping = json.load(f)
        return mapping


def add_category(description, cost, date, purchase_mapping, account_mapping):
    loop = 0
    while loop == 0:
        print("The description:"+description+" with cost: "+cost+"on date: "+str(date) +
              ": is not mapped. Please provide mapping to existing account.")
        print(account_mapping)

        user_input = input("--> ")
        if user_input in account_mapping:
            purchase_mapping[description] = user_input
            loop = 1
        else:
            print("Didn't Match valid account.")

    with open('mapping.json', 'w') as f:
        json.dump(purchase_mapping, f)

    return purchase_mapping


def get_info(purchase_amt):

    if purchase_amt > 0:
        destination = "Income:"
    else:
        destination = "Expenses:"

    return destination

