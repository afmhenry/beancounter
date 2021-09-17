import os
import sys
from importers.danskebank import DanskeBankImporter

# beancount doesn't run from this directory
sys.path.append(os.path.dirname(__file__))

# todo: find out how to initialize bank accounts programtically.

CONFIG = [
    DanskeBankImporter.Importer('Assets:DanskeBank:Checking'),
]