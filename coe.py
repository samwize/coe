import urllib
import urllib2
from time import sleep, gmtime, strftime
from datetime import datetime, timedelta
from pprint import pprint
from pytz import timezone
from bs4 import BeautifulSoup
import re
import json

fmt = '%Y-%m-%d %H%M'
gmt8tz = timezone('Asia/Singapore')
bid_end_time_regex = re.compile('Bidding will end on (.*?) hrs')
bid_end_time_fmt = '%d/%m/%Y %H:%M'
bid_current_time_regex = re.compile('Bidding status as at (.*?) hrs')
bid_current_time_fmt = '%d/%m/%Y %H:%M:%S.%f'


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
        s = json.dumps(json_dict)
        myfile.write(s)



# Parse html and return a dict
# end_at
# datetime
# status = running | finalized
# cat_a
#   price
#   quota
#   bids
# cat_b/c/d/e
def parse(html):
    soup = BeautifulSoup(html)
    
    # json will hold the json to return
    json = dict()

    bid_end_time_str = bid_end_time_regex.findall(soup.p.string)[0]
    bid_end_time = datetime.strptime(bid_end_time_str, bid_end_time_fmt)
    json['end_at'] = bid_end_time

    bid_current_time_str = bid_current_time_regex.findall(soup.h3.string)[0]
    bid_current_time = datetime.strptime(bid_current_time_str, bid_current_time_fmt)
    json['datetime'] = bid_current_time
    
    cats = ['cat_a', 'cat_b', 'cat_c', 'cat_d', 'cat_e']
    for i in range(0, 5):
        # Print for each of the 5 category
        # print soup.find_all('td')[i*5 + 0].string
        # print soup.find_all('td')[i*5 + 1].string
        # print soup.find_all('td')[i*5 + 2].string
        # print soup.find_all('td')[i*5 + 3].string
        # print soup.find_all('td')[i*5 + 4].string
        # print '-' *20
        
        cat = dict()
        cat['price'] = soup.find_all('td')[i*5 + 2].string
        cat['quota'] = soup.find_all('td')[i*5 + 3].string
        cat['bids'] = soup.find_all('td')[i*5 + 4].string
        json[cats[i]] = cat

    print json
    return json
        



    

while True:
    # crawl every minute
    crawl()
    sleep(60)

    # parse(open('./html/2013-03-25 1215.html'))
    # sleep(120)

