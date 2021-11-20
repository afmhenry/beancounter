 # Beancounter
 
## Usage: 

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

## General to do:
* find out how to handle selling at different cost basis
* See what customization is possible with fava--what views are most valuable for me. 
* See what options there are for a [query interface](https://beancount.github.io/docs/beancount_query_language.html) and how that can be used to have fine tune control.


# Current Output
![Fava Assets](/media/fava_assets.png?raw=true "Fava Assets")


## Known issues:
* unrealized gains will not be able to find a price for the entity in the same "start" run as when it was purchased. Run move.sh, then re-run start.sh to resolve. 
* marketstack api has 100 requests per month--I have to use 2 per stock to get the price. Probably enough, but while testing I used all pretty quick. 
* round is inconsistent--I plan to work on cleaning that up 


### If you want to edit this or build something similar:

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