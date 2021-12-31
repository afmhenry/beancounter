import os
import sys

# beancount doesn't run from this directory
sys.path.append(os.path.dirname(__file__))

# importers located in the importers directory
from importers.danskebank import DanskeBankImporter
from importers.nordnet import NordnetImporter
from importers.saxobank import SaxoBankImporter
from importers.schwab import CharlesSchwabImporter
from importers.external import UnrealizedGainsImporter
from importers.payslips import VismaPayslipImporter

CONFIG = [
    VismaPayslipImporter.Importer(
        'Income:Work:GrossSalary',
        'Assets:DanskeBank:Checking',
        'Expenses:Tax:',
        'Assets:Investment:Pension:',
        'Income:Pension:',
        'Expenses:Consumption:Lunch'
    ),
    DanskeBankImporter.Importer('Assets:DanskeBank:Checking'),
    NordnetImporter.Importer(
        'Assets:Investment:Nordnet:Depot:Cash',
        'Expenses:Trading:Commissions',
        'Income:Investment:Nordnet:PnL:Sales',
        'Income:Investment:Nordnet:PnL:Dividends',
        'Expenses:Tax'
    ),
    SaxoBankImporter.Importer(
        'Assets:Investment:SaxoBank:Depot:Cash',
        'Expenses:Trading:Commissions',
        'Income:Investment:SaxoBank:PnL:Sales',
        'Income:Investment:SaxoBank:PnL:Dividends',
        'Expenses:Tax'
    )
]

CONFIGPLACEHOLDER = [
    DanskeBankImporter.Importer('Assets:DanskeBank:Checking'),
    NordnetImporter.Importer(
        'Assets:Investment:Nordnet:Depot:Cash',
        'Expenses:Trading:Commissions',
        'Income:Investment:Nordnet:PnL:Sales',
        'Income:Investment:Nordnet:PnL:Dividends',
        'Expenses:Tax'
    ),
    SaxoBankImporter.Importer(
        'Assets:Investment:SaxoBank:Depot:Cash',
        'Expenses:Trading:Commissions',
        'Income:Investment:SaxoBank:PnL:Sales',
        'Income:Investment:SaxoBank:PnL:Dividends',
        'Expenses:Tax'
    ),
    CharlesSchwabImporter.Importer(
        'Assets:Investment:Schwab:Depot:Cash',
        'Expenses:Trading:Commissions',
        'Income:Investment:Nordnet:PnL:Sales',
        'Income:Investment:Nordnet:PnL:Dividends',
        'Expenses:Tax'
    ),
    UnrealizedGainsImporter.Importer("No input needed right now"),
]