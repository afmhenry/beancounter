import os
import sys

# beancount doesn't run from this directory
sys.path.append(os.path.dirname(__file__))

# importers located in the importers directory
from importers.danskebank import DanskeBankImporter
from importers.nordnet import NordnetImporter

CONFIG = [
    DanskeBankImporter.Importer('Assets:DanskeBank:Checking'),
    NordnetImporter.Importer('Assets:Nordnet:Depot:Cash'),
]