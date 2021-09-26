 # Beancounter
 
Usage: 

* Open the scripts folder
* Decide which operation you want to do:
  * `test.sh`: Test the purchase classifier on the bank account input file, build a mapping to be used later.
  * `start.sh`: Apply the built mapping to your beancount file
  * `fava.sh`: Visualize the provided beancount file with fava. 

General to do:
* confirm mapping works as intended.
* figure out data flow--taking in generic file names and moving them for safekeeping in folders after ingress.
* See what customization is possible with fava--what views are most valuable for me. 
* See what options there are for a [query interface](https://beancount.github.io/docs/beancount_query_language.html) and how that can be used to have fine tune control.


Based on source code from here:
https://github.com/beancount/beancount/tree/v2/examples/ingest/office
and documentation here:
https://docs.google.com/document/d/11EwQdujzEo2cxqaF5PgxCEZXWfKKQCYSMfdJowp_1S8/edit#
