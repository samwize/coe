coe
===

Crawl Singapore LTA onemotoring website for the open bidding live results. COE = Certificate of Entitlement = A piece of $80,000 paper needed to own a car in Singapore.



Model
-----


## Round ##

This model a bidding round eg. March 2013 2nd Round

Properties:

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



## Bid ##

This model an instance of a running bid at a specific time.

Properties:

- round_id
- bid_on
- cat
- price
- bids



