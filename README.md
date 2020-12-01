# Spentless. Server
* [![Build Status](https://travis-ci.com/SpentlessInc/spentless-server.svg?branch=master)](https://travis-ci.com/SpentlessInc/spentless-server) **Productions**
* [![Build Status](https://travis-ci.com/SpentlessInc/spentless-server.svg?branch=staging)](https://travis-ci.com/SpentlessInc/spentless-server) **Staging**

# Description
API documentation: http://spentless.herokuapp.com/v1/api


The main API server includes:
* auth operations
* get/update budget information
* get/create/update/delete limit of budget category
* list of transactions
* transactions reports
* activating third-party services (monobank, telegram)

# How to run?
Follow the instruction placed in [spentless-infrastructure](https://github.com/SpentlessInc/spentless-infrastructure).

# Scripts
* cache_cleanup.py - clean up cache item by keys. Example: `python cache_cleanup.py mcc_codes test_key another key`
* database_seed.py - seed database data. Example: `python seed.py`
