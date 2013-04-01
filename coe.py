import urllib
import urllib2
from time import sleep, gmtime, strftime
from datetime import datetime, timedelta
from pprint import pprint
from pytz import timezone
from bs4 import BeautifulSoup
import re
import json
import os
from pymongo import MongoClient


# Some of the datetime formats
fmt = '%Y-%m-%d %H%M'
gmt8tz = timezone('Asia/Singapore')
datetime_short_fmt = '%d/%m/%Y %H:%M'
datetime_full_fmt = '%d/%m/%Y %H:%M:%S.%f'

# Regex for parsing
bid_end_time_regex = re.compile('Bidding will end on (.*?) hrs')
bid_current_time_regex = re.compile('Bidding status as at (.*?) hrs')
this_round_regex = re.compile('(.*?) Open Bidding Exercise has ended on (.*?) hrs')

# Set to true to print logs
DEBUG = False

# Setup MongoDB
client = MongoClient()
db = client.coe
rounds = db.rounds
bids = db.bids



# Crawl the COE website
# Save to html
# Return the html (as string)
def crawl():
    print '.'
    req = urllib2.Request('http://www.onemotoring.com.sg/1m/coe/coeDetail.html')
    response = urllib2.urlopen(req)
    data = response.read()
    # print data

    # Write to file
    local_time = gmt8tz.localize(datetime.now())
    file = open('./html/' + local_time.strftime(fmt) + '.html', "w+")
    file.write(data)
    file.close()

    # Write to json  
    with open("./data/database.json", "a") as myfile:
        json_dict = parse(data)
        # Use this 1-liner encoder (http://stackoverflow.com/a/2680060/242682)
        dthandler = lambda obj: obj.isoformat() if isinstance(obj, datetime) else None
        s = json.dumps(json_dict, default=dthandler)
        if s is not None and s != 'null':
            myfile.write(s + "\n")

    return data



# Parse html and return a dict
def parse(html):
    # Recognize the bidding still running or ended
    if html.find('Bidding Exercise has ended') == -1:
        # Not ended. It's running.
        json = parse_running(html)
    else:
        # It's ended.
        json = parse_ended(html)

    if DEBUG:
        print json

    return json



# Parse for a bidding round that is currently running
# status = 'running'
# name = eg 'March 2nd Round'
# end_on
# bid_on
# updated_on = now
# cat_a
#   price
#   quota
#   bids
# cat_b/c/d/e
def parse_running(html):
    try:
        soup = BeautifulSoup(html)
        
        # json will hold the json to return
        json = dict()
        json['status'] = 'running'

        bid_end_time_str = bid_end_time_regex.findall(soup.p.string)[0]
        bid_end_time = datetime.strptime(bid_end_time_str, datetime_short_fmt)
        json['end_on'] = bid_end_time

        bid_current_time_str = bid_current_time_regex.findall(soup.h3.string)[0]
        bid_current_time = datetime.strptime(bid_current_time_str, datetime_full_fmt)
        json['bid_on'] = bid_current_time
        
        json['updated_on'] = datetime.now()

        cats = ['cat_a', 'cat_b', 'cat_c', 'cat_d', 'cat_e']
        for i in range(0, 5):
            if DEBUG:
                # Print for each of the 5 category
                print soup.find_all('td')[i*5 + 0].string
                print soup.find_all('td')[i*5 + 1].string
                print soup.find_all('td')[i*5 + 2].string
                print soup.find_all('td')[i*5 + 3].string
                print soup.find_all('td')[i*5 + 4].string
                print '-' *20
                
            cat = dict()
            cat['price'] = soup.find_all('td')[i*5 + 2].string
            cat['quota'] = soup.find_all('td')[i*5 + 3].string
            cat['bids'] = soup.find_all('td')[i*5 + 4].string
            json[cats[i]] = cat

        if DEBUG:
            print json

        return json
        
    except Exception, e:
        # raise e
        # Just ignore
        pass



# Parse the website when bidding ended
# status = 'ended'
# name = eg 'March 2nd Round'
# end_on = datetime
# updated_on = now
# cat_a
#   qp
#   pqp
#   quota
#   bids_received
#   bids_successful
#   bids_unsuccessful
#   bids_unused
# cat_b/c/d/e
def parse_ended(html):
    try:
        soup = BeautifulSoup(html)
        
        # json will hold the json to return
        json = dict()
        json['status'] = 'ended'

        this_round_array = this_round_regex.findall(soup.p.string)[0]
        name_str = this_round_array[0]
        json['name'] = name_str

        end_on_str = this_round_array[1]
        end_on = datetime.strptime(end_on_str, datetime_short_fmt)
        json['end_on'] = end_on

        json['updated_on'] = datetime.now()
        
        cats = ['cat_a', 'cat_b', 'cat_c', 'cat_d', 'cat_e']
        for i in range(0, 5):
            if DEBUG:
                # Print for each of the 5 category
                print soup.find_all('td')[i*5 + 0].string
                print soup.find_all('td')[i*5 + 1].string
                print soup.find_all('td')[i*5 + 2].string
                print soup.find_all('td')[i*5 + 3].string
                print soup.find_all('td')[i*5 + 4].string
                print '-' *20
                
            cat = dict()
            cat['quota']    = soup.find_all('td')[i*5 + 2].string
            cat['qp']       = soup.find_all('td')[i*5 + 3].string
            cat['pqp']      = soup.find_all('td')[i*5 + 4].string
            json[cats[i]]   = cat

        for i in range(0, 5):
            if DEBUG:
                # Print for each of the 5 category
                print soup.find_all('td')[26 + i*6 + 0].string
                print soup.find_all('td')[26 + i*6 + 1].string
                print soup.find_all('td')[26 + i*6 + 2].string
                print soup.find_all('td')[26 + i*6 + 3].string
                print soup.find_all('td')[26 + i*6 + 4].string
                print soup.find_all('td')[26 + i*6 + 5].string
                print '-' *20
                
            cat = json[cats[i]]
            cat['bids_received']        = soup.find_all('td')[26 + i*6 + 2].string
            cat['bids_successful']      = soup.find_all('td')[26 + i*6 + 3].string
            cat['bids_unsuccessful']    = soup.find_all('td')[26 + i*6 + 4].string
            cat['bids_unused']          = soup.find_all('td')[26 + i*6 + 5].string

        if DEBUG:
            print json

        return json

    except Exception, e:
        # raise e
        # Just ignore
        pass




# Read all the html in ./html and save to ./data/database.json
def parse_all_html_to_json():
    # For every html file
    # Save to database.json
    i = 0
    for f in os.listdir('./html'):
        if (f.endswith('.html')):
            i += 1
            print '>> ' + str(i) + ' :' + f
            json_dict = parse(open('./html/' + f).read())
            # Write to json  
            with open("./data/database.json", "a") as myfile:
                # Use this 1-liner encoder (http://stackoverflow.com/a/2680060/242682)
                dthandler = lambda obj: obj.isoformat() if isinstance(obj, datetime) else None
                s = json.dumps(json_dict, default=dthandler)
                if s is not None and s != 'null':
                    myfile.write(s + "\n")


# Read ./data/database.json and add to mongo db
def insert_json_to_db():
    with open('./data/database.json') as f:
        for json_str in f:
            j = json.loads(json_str)
            # TODO
            # if j['status'] == 'running':
            #     # status = running
            #     # Add a bid
            # else:
            #     # status = ended
            #     # Add a round
            #     r
            #     round.insert()
        

while True:
    # Crawl every minute
    # crawl()
    # sleep(60)

    # TESTING
    # Bidding Running
    # parse(open('./html/2013-03-25 1215.html').read())
    # Bidding Ended
    # parse(open('./html/2013-04-01 1627.html').read())
    # parse_all_html_to_json()
    insert_json_to_db()
    sleep(12000)

    