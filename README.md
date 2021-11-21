# Beancounter
 

# Current Results


## Knowing where my money goes

Beancount requires that transactions balance--that is, you categorize all parts of a transaction, and those 
categories are custom, queryable, and sortable. Custom currencies mean you can hold stock with a relation to fiat 
currencies, and still be aware of the details of the holding

## Human-readable storage format with rich & custom detail

![](media/beancount_buy_stock.png)
<p align=center><i>Buying Stock</i></p>

![](media/beancount_sell_stock.png)
<p align=center><i>Selling Stock</i></p>

![](media/beancount_dividend_income.png)
<p align=center><i>Gaining dividends from stock</i></p>

## Flexible overview of my own category spending:
![Fava Groceries](media/fava_groceries.png?raw=true "Fava Assets")

## Overview of value of Stock Holdings, Unrealized profit, Cash Holdings.

![Fava Assets](media/fava_assets.png?raw=true "Fava Assets")

## Overview of income and sources of it

![Fava Income](media/fava_income.png?raw=true "Fava Assets")

## Near full automation

Only manual steps are:
* Download relevant files from your bank
* Move them to the data folder
* The 3 below scripts could be run as one, but as you may want to:
    * Create a new account during mapping
    * verify the account balance, before moving the imported files.
* Run the mapping script
* Run the start script
* Run the move script.
    
This can be done as frequently as you want, but I wouldn't see a need to do it more than monthly


# Usage: 

* Open the scripts folder
* Decide which operation you want to do:
  * `map.sh`: Test the purchase classifier on the bank account input file, build a mapping to be used later. 
  * Does not create beancount file.
  * `start.sh`: Apply the built mapping to your beancount file, consume files
  * `check.sh`: Only check the file: if you hear nothing that is good :)
  * `fava.sh`: Visualize the provided beancount file with fava. 
  * `move.sh`: Move your ingress files from `data`folder to structured folders after ingestion. -n flag is a test run, 
  * so you can safely see if you have implemented the file_account function on the importer as expected. 
  * `test.sh`: Test smaller parts of the code to avoid mapping or start processes.  

Paths present in the scripts may need adjusting.

You will also have to chmod u+x the scripts. 

Adding a new importer is pretty trivial--you have 3 examples of how to handle different formats. Copy, paste, 
test using run mapping script :)

Make sure to get the right encoding, accepted values can be found here:
https://docs.python.org/3/library/codecs.html#encodings-and-unicode

You can determine what encoding the downloaded bank file is in, by running this in the cli. 
  
```
>> file filename
>> 2021-11-14.Nordnet-Depot-Transactions.csv: Little-endian UTF-16 Unicode text, with very long lines, with CRLF line terminators
```

# General to do:
* find out how to handle selling at different cost basis
* See what customization is possible with fava--what views are most valuable for me. 
* See what options there are for a [query interface](https://beancount.github.io/docs/beancount_query_language.html) and how that can be used to have fine tune control.



# Known issues:
* unrealized gains will not be able to find a price for the entity in the same "start" run as when it was purchased. 
To get the price, after running, execute move.sh, then re-run start.sh to resolve. 
* marketstack api has 100 requests per month--I have to use 2 per stock to get the price. Probably enough, but while 
testing I used all pretty quick. 
* round is inconsistent--I plan to work on cleaning that up 


# If you want to edit this or build something similar:

Motivation:
https://beancount.github.io/docs/command_line_accounting_in_context.html#motivation

Getting Started:

https://beancount.github.io/docs/getting_started_with_beancount.html

Based on source code from here:
https://github.com/beancount/beancount/tree/v2/examples/ingest/office


Documentation here:
https://docs.google.com/document/d/11EwQdujzEo2cxqaF5PgxCEZXWfKKQCYSMfdJowp_1S8/edit#

Trading Details:
https://beancount.github.io/docs/trading_with_beancount.html