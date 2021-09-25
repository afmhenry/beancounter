import json
import tkinter as tk


def get_accounts():
    accounts = []
    with open('accounts.beancount') as f:
        for line in f:
            if "open" in line:
                line = line.split(" ")
                accounts.append(line[2].replace("\n", ""))
    return accounts


def get_categories():
    with open('mapping.json') as f:
        mapping = json.load(f)
        return mapping


def add_category(description, cost, date, purchase_mapping, account_mapping):
    # Create object
    root = tk.Tk()

    # Adjust size
    root.geometry("200x200")

    # Change the label text
    def show():
        label.config(text=clicked.get())

    # Dropdown menu options

    label = tk.Label(text=description + "\n" + cost + "\n" + str(date),
                     foreground="white",
                     background="black",
                     width=20,
                     height=6
                     )
    label.pack()
    # datatype of menu text
    clicked = tk.StringVar()

    # initial menu text
    clicked.set(account_mapping[0])

    # Create Dropdown menu
    drop = tk.OptionMenu(root, clicked, *account_mapping)
    drop.pack()

    # Create button, it will change label text
    button = tk.Button(root, text="Select", command=show).pack()

    # Create Label
    label = tk.Label(root, text=" ")
    label.pack()

    # Execute tkinter
    root.mainloop()
    # window = tk.Tk()
    # label = tk.Label(text="Category needs assigning.",
    #                  foreground="white",
    #                  background="black",
    #                  width=20,
    #                  height=10
    #                  )
    # label.pack()
    #
    # button = tk.Button(
    #     text="Assign Category",
    #     width=15,
    #     height=3,
    #     bg="blue",
    #     fg="purple",
    # )

    loop = 0
    while loop == 0:
        print("The description:" + description + " with cost: " + cost + "on date: " + str(date) +
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
