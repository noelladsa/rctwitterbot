import twython
import sys
import json
from markov import Markov
from datetime import datetime, timedelta
import random
from pymarkovchain import MarkovChain

RESULTS_PER_USER = 100
FINAL_TWEET_MIN_LENGTH = 50
tweetList = []
api_key, api_secret, access_key, access_token = sys.argv[1:]

#TBD make the api call to get the RC twitter handles
twitterHandleList = ["senojeyawd", "anyharder", "matthewisabel", "csofiatti", "adampash", "myflow", "feinomenon", "punchagan", "0xtristan", "clairetreyz", "dmlicht", "kkristensen", "arsentumanyan", "bhushanlodha", "coreylynch", "thingiebox", "balau", "alexandrinaNYC", "iamstephsamson", "RadicalZephyr", "gelstudios", "DanielleSucher", "stoneGksp", "doridoidea", "cjbprime", "czaplic", "leah_steinberg", "crux", "bruslim", "astrieanna", "GinaSchmalzle", "podsnap", "martintornwall", "davidad", "mveytsman", "tomca32", "clint_newsom", "danluu", "angusnb", "nancyorgan", "pgbovine", "pchiusano", "laurensperber", "kylewpppd", "peterseibel", "khaullen", "glyph", "ambimorph", "erichammy", "trihybrid", "miclovich", "zachdex", "pvmoura", "MacLaneWilkison", "georgewking", "lawrensm", "buybackoff", "saintrosa", "stuart_san", "cirsteve", "ifosteve", "hausdorff_space", "supacliny", "brannerchinese", "rpsoko", "r00k", "zeigenvector", "ffwang2", "ox", "jdherg", "dankoslow", "heddle317", "nerdneha", "roborative", "BrentNAtkinson", "HeidiKasemir", "chrisedgemon", "kaizokuace", "kisharichardson", "kategeek", "NathanMichalov", "guilload", "nycgwailou", "dy_dx_", "georgicodes", "tansyarron", "slendrmeans", "efkv", "_jak", "vjuutilainen", "shieldsofdreams", "dzucconi", "mljungblad", "gredaline", "marinftw", "grstearns", "billiamram", "deckycoss", "mariapacana", "tmcdemus", "marqs_m", "bglusman", "deanna_hood", "paulvstheworld", "gnclmorais", "gideondresdner", "swanpants", "lunacodess", "chimeracoder", "damiankao", "codee", "srmor", "linse", "buttsmeister", "KarenPunkPunk", "miriamlauter", "rowdyrabbit", "petefrance", "TedLee", "rawrjustin", "corydominguez", "chris_j_ryan", "vise890", "rodarmor", "tylersimko", "kanja", "rsnous", "nathanmarz", "webyrd", "jyli7", "gnitlis", "joystate"]

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

#uses the library pymarkovchain with sourcecode here: https://github.com/TehMillhouse/PyMarkovChain
def getMarkovSyntetizedText():
    # Create an instance of the markov chain. By default, it uses MarkovChain.py's location to
    # store and load its database files to. You probably want to give it another location, like so:
    mc = MarkovChain("./markov")
    # To generate the markov chain's language model, in case it's not present
    mc.generateDatabase(".".join(tweetList))
    # To let the markov chain generate some text, execute
    return mc.generateString()

def getFilteredSynthesizedTweet():
    notGoodSynthesizedMsg = True
    generatedTweet = getMarkovSyntetizedText()
    print generatedTweet
    while len(generatedTweet) < FINAL_TWEET_MIN_LENGTH or "http://" in generatedTweet:
        generatedTweet = getFilteredSynthesizedTweet()
    return generatedTweet   

if __name__ == '__main__':
    twy = twython.Twython(api_key,api_secret,access_key, access_token)
    twitterHandles = chunks(twitterHandleList, 15)

    for handlesChunk in twitterHandles:  
        data = twy.search(q=createSearchQuery(handlesChunk), since=getFormattedYesterdayDate(), count=RESULTS_PER_USER, exclude="replies")
        addTwittersFromSearch(data)

    random.shuffle(tweetList)
    twy.update_status(status=getFilteredSynthesizedTweet())


