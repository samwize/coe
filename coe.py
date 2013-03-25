import urllib
import urllib2
from time import sleep, gmtime, strftime
from datetime import datetime, timedelta
from pprint import pprint
from pytz import timezone

fmt = '%Y-%m-%d %H%M'
gmt8tz = timezone('Asia/Singapore')

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
    

while True:
    # crawl every minute
    crawl()
    sleep(60)