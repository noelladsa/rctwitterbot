import twython
import sys
import json
from markov import Markov
from datetime import datetime, timedelta
import random
from pymarkovchain import MarkovChain

RESULTS_PER_USER = 100
FINAL_TWEET_MIN_LENGTH = 50
tweet_list = []
api_key, api_secret, access_key, access_token = sys.argv[1:]

def add_twitters_from_search(twitter_response_dict):
    for tweet in twitter_response_dict["statuses"]:
         tweet_list.append(tweet["text"])


def chunks(l, n):
    """Yield successive n-sized chunks from l."""
    for i in xrange(0, len(l), n):
        yield l[i:i+n]

def create_search_query(handlesList):
    return "from:" + "+OR+from:".join(handlesList)

def get_formatted_yesterday_date():
    yesterday_date = datetime.now() - timedelta(days=2)
    return yesterday_date.strftime("%Y-%m-%d")

#uses the library pymarkovchain with sourcecode here: https://github.com/TehMillhouse/PyMarkovChain
def get_markov_syntetized_text():
    # Create an instance of the markov chain. By default, it uses MarkovChain.py's location to
    # store and load its database files to. You probably want to give it another location, like so:
    mc = MarkovChain("./markov")
    # To generate the markov chain's language model, in case it's not present
    mc.generateDatabase(".".join(tweet_list))
    # To let the markov chain generate some text, execute
    return mc.generateString()

#runs the markov chain alg until it finds a synthesized msgs that is more then 50 chars long and does not contain links
def get_filtered_synthesized_tweet():
    generated_tweet = get_markov_syntetized_text()
    print generated_tweet
    while len(generated_tweet) < FINAL_TWEET_MIN_LENGTH or "http://" in generated_tweet or "@" in generated_tweet:
        generated_tweet = get_markov_syntetized_text()
    return generated_tweet   

def update_twitter(handles):
    twy = twython.Twython(api_key,api_secret,access_key, access_token)
    #splits the handles list in sublists of size 15 and does a multiple user search for each sublist
    twitter_handles = chunks(twitterHandleList, 15)

    for handles_chunk in twitter_handles:  
        data = twy.search(q=create_search_query(handles_chunk), since=get_formatted_yesterday_date(), count=RESULTS_PER_USER, exclude="replies")
        add_twitters_from_search(data)

    random.shuffle(tweet_list)
    print(get_filtered_synthesized_tweet())
    #twy.update_status(status=get_filtered_synthesized_tweet())

if __name__ == '__main__':
    twitterHandleList = ["senojeyawd", "anyharder", "matthewisabel", "csofiatti", "adampash", "myflow", "feinomenon", "punchagan", "0xtristan", "clairetreyz", "dmlicht", "kkristensen", "arsentumanyan", "bhushanlodha", "coreylynch", "thingiebox", "balau", "alexandrinaNYC", "iamstephsamson", "RadicalZephyr", "gelstudios", "DanielleSucher", "stoneGksp", "doridoidea", "cjbprime", "czaplic", "leah_steinberg", "crux", "bruslim", "astrieanna", "GinaSchmalzle", "podsnap", "martintornwall", "davidad", "mveytsman", "tomca32", "clint_newsom", "danluu", "angusnb", "nancyorgan", "pgbovine", "pchiusano", "laurensperber", "kylewpppd", "peterseibel", "khaullen", "glyph", "ambimorph", "erichammy", "trihybrid", "miclovich", "zachdex", "pvmoura", "MacLaneWilkison", "georgewking", "lawrensm", "buybackoff", "saintrosa", "stuart_san", "cirsteve", "ifosteve", "hausdorff_space", "supacliny", "brannerchinese", "rpsoko", "r00k", "zeigenvector", "ffwang2", "ox", "jdherg", "dankoslow", "heddle317", "nerdneha", "roborative", "BrentNAtkinson", "HeidiKasemir", "chrisedgemon", "kaizokuace", "kisharichardson", "kategeek", "NathanMichalov", "guilload", "nycgwailou", "dy_dx_", "georgicodes", "tansyarron", "slendrmeans", "efkv", "_jak", "vjuutilainen", "shieldsofdreams", "dzucconi", "mljungblad", "gredaline", "marinftw", "grstearns", "billiamram", "deckycoss", "mariapacana", "tmcdemus", "marqs_m", "bglusman", "deanna_hood", "paulvstheworld", "gnclmorais", "gideondresdner", "swanpants", "lunacodess", "chimeracoder", "damiankao", "codee", "srmor", "linse", "buttsmeister", "KarenPunkPunk", "miriamlauter", "rowdyrabbit", "petefrance", "TedLee", "rawrjustin", "corydominguez", "chris_j_ryan", "vise890", "rodarmor", "tylersimko", "kanja", "rsnous", "nathanmarz", "webyrd", "jyli7", "gnitlis", "joystate"]
    update_twitter(twitterHandleList)


