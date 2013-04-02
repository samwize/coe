## Introduction ##

This script crawls Singapore LTA onemotoring website for the open bidding live results. COE = Certificate of Entitlement = A piece of $80,000 paper needed to own a car in Singapore.


## Setting up ##

You can run this scrip on your local machine or on Dotcloud. The project has the necessary setup for Dotcloud instance.

If you are running on your local machine, run `mongod` (we use MongoDB for database), clone this git project, then:

```
pip install -r requirements.txt
python coe.py -d
```

The -d is to run the script as a daemon (background process). 

For Dotcloud, simply create an app then `dotcloud push`.


## Model ##


### Round ###

This model a bidding round eg. March 2013 2nd Round

- name
- status = running | ended
- end_on
- cat_a/b/c/d/e
	- cat
	- qp
	- pqp
	- quota
	- bids_received
	- bids_successful
	- bids_unsuccessful
	- bids_unused



### Bid ###

This model an instance of a running bid at a specific time.

- round_id
- bid_on
- cat
- price
- bids
- quota



