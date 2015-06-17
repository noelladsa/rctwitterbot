import twython
import sys
import json
from markov import Markov
from datetime import datetime, timedelta
import random

RESULTS_PER_USER = 100
tweetList = []
api_key, api_secret, access_key, access_token = sys.argv[1:]

twitterHandleList = ["senojeyawd",  "anyharder"]

def addTwittersFromSearch(twitterResponseDict):
    for tweet in twitterResponseDict["statuses"]:
         tweetList.append(tweet["text"])


def chunks(l, n):
    """Yield successive n-sized chunks from l."""
    for i in xrange(0, len(l), n):
        yield l[i:i+n]

def createSearchQuery(handlesList):
    return "from:" + "+OR+from:".join(handlesList)

def getFormattedYesterdayDate():
    yesterdayDate = datetime.now() - timedelta(days=2)
    return yesterdayDate.strftime("%Y-%m-%d")


twy = twython.Twython(api_key,api_secret,access_key, access_token)
twitterHandles = chunks(twitterHandleList, 15)

for handlesChunk in twitterHandles:  
    data = twy.search(q=createSearchQuery(handlesChunk), since=getFormattedYesterdayDate(), count=RESULTS_PER_USER, exclude="replies")
    #print(json.dumps(data, encoding="utf-8"))
    addTwittersFromSearch(data)

random.shuffle(tweetList)
print  ".".join(tweetList)

# file_ = open('/Users/erisa/hackerschool/rctwitterbot/markov_input.txt')


# markov = Markov(file_)

# printmarkov.generate_markov_text()

