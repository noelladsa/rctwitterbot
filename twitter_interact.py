import twython
import sys
import json
from datetime import datetime, timedelta
import random
from markov_aparrish import char_level_generate
from markov_aparrish import word_level_generate
import os

RESULTS_PER_USER = 100
FINAL_TWEET_MIN_LENGTH = 100
FINAL_TWEET_MAX_LENGTH = 140
api_key=os.environ.get('TWITTER_API_KEY', None)
api_secret=os.environ.get('TWITTER_API_SECRET', None)
access_key= os.environ.get('TWITTER_ACCESS_KEY', None)
access_token = os.environ.get('TWITTER_ACCESS_TOKEN', None)

def add_twitters_from_search(twitter_response_dict, tweet_list):
    for tweet in twitter_response_dict["statuses"]:
        indices = []
        entities = tweet["entities"]
        mention_list = entities["user_mentions"]
        url_list = entities["urls"]
        if mention_list:
            for mention in mention_list:
                indices.append((mention["indices"][0], mention["indices"][1]))
        if url_list:
            for url in url_list:
                indices.append((url["indices"][0], url["indices"][1]))
        #sorts in place indices list by the first index      
        indices.sort(key=lambda tup: tup[1]) 
        tweet_list.append(filter_mentions_and_urls(indices, tweet["text"]))

def filter_mentions_and_urls(indices, tweet_text):
    trimmed_chars = 0
    for index_tuple in indices:
        tweet_text = tweet_text[:(index_tuple[0]-trimmed_chars)] + "" + tweet_text[(index_tuple[1]-trimmed_chars):]
        trimmed_chars = trimmed_chars + (index_tuple[1] - index_tuple[0])
    return tweet_text

def chunks(l, n):
    """Yield successive n-sized chunks from l."""
    for i in xrange(0, len(l), n):
        yield l[i:i+n]

def create_search_query(handlesList):
     return "from:" + "+OR+from:".join(handlesList)

def get_formatted_yesterday_date():
    yesterday_date = datetime.now() - timedelta(days=2)
    return yesterday_date.strftime("%Y-%m-%d")

#uses this markov implementation:
#https://github.com/aparrish/rwet-examples/blob/master/ngrams/markov.py
def get_markov_syntetized_tweet(tweet_list):
    return (" ").join(word_level_generate(tweet_list, 2, count=2))

def get_filtered_synthesized_tweet(tweet_list):
    generated_tweet = get_markov_syntetized_tweet(tweet_list)
    while len(generated_tweet) < FINAL_TWEET_MIN_LENGTH or len(generated_tweet) > FINAL_TWEET_MAX_LENGTH or "http://" in generated_tweet or "https://" in generated_tweet:
        #print generated_tweet
        generated_tweet = get_markov_syntetized_tweet(tweet_list)
    return generated_tweet   

def update_twitter(handles):
    tweet_list = []
    twy = twython.Twython(api_key,api_secret,access_key, access_token)
    #splits the handles list in sublists of size 15 and does a multiple user search for each sublist
    twitter_handles = chunks(handles, 15)

    for handles_chunk in twitter_handles:  
        data = search_tweets(twy, handles_chunk)
        #print(json.dumps(data, encoding="utf-8"))
        add_twitters_from_search(data, tweet_list)
        next_max_id = get_next_max_id(data)
        while next_max_id > 0:
            data = search_tweets(twy, handles_chunk, next_max_id)
            add_twitters_from_search(data, tweet_list)
            next_max_id = get_next_max_id(data)
    random.shuffle(tweet_list)
    #print "\n".join(tweet_list)
    #print "Final tweet:" + get_filtered_synthesized_tweet(tweet_list)
    twy.update_status(status=get_filtered_synthesized_tweet())

def search_tweets(twython, handles_chunk, next_max_id=0):
    if next_max_id == 0:
        return twython.search(q=create_search_query(handles_chunk), since=get_formatted_yesterday_date(), exclude="retweets", count=RESULTS_PER_USER, exclude_replies=1)
    else:
        return twython.search(q=create_search_query(handles_chunk), since=get_formatted_yesterday_date(), exclude="retweets", count=RESULTS_PER_USER, exclude_replies=1, max_id=next_max_id)


def get_next_max_id(results):
    # Get the next max_id
    try:
        # Parse the data returned to get max_id to be passed in consequent call.
        next_results_url_params    = results['search_metadata']['next_results']
        return next_results_url_params.split('max_id=')[1].split('&')[0]
    except:
        # No more next pages
        return 0

if __name__ == '__main__':
    twitterHandleList = ["senojeyawd", "anyharder", "matthewisabel", "csofiatti", "adampash", "myflow", "feinomenon", "punchagan", "0xtristan", "clairetreyz", "dmlicht", "kkristensen", "arsentumanyan", "bhushanlodha", "coreylynch", "thingiebox", "balau", "alexandrinaNYC", "iamstephsamson", "RadicalZephyr", "gelstudios", "DanielleSucher", "stoneGksp", "doridoidea", "cjbprime", "czaplic", "leah_steinberg", "crux", "bruslim", "astrieanna", "GinaSchmalzle", "podsnap", "martintornwall", "davidad", "mveytsman", "tomca32", "clint_newsom", "danluu", "angusnb", "nancyorgan", "pgbovine", "pchiusano", "laurensperber", "kylewpppd", "peterseibel", "khaullen", "glyph", "ambimorph", "erichammy", "trihybrid", "miclovich", "zachdex", "pvmoura", "MacLaneWilkison", "georgewking", "lawrensm", "buybackoff", "saintrosa", "stuart_san", "cirsteve", "ifosteve", "hausdorff_space", "supacliny", "brannerchinese", "rpsoko", "r00k", "zeigenvector", "ffwang2", "ox", "jdherg", "dankoslow", "heddle317", "nerdneha", "roborative", "BrentNAtkinson", "HeidiKasemir", "chrisedgemon", "kaizokuace", "kisharichardson", "kategeek", "NathanMichalov", "guilload", "nycgwailou", "dy_dx_", "georgicodes", "tansyarron", "slendrmeans", "efkv", "_jak", "vjuutilainen", "shieldsofdreams", "dzucconi", "mljungblad", "gredaline", "marinftw", "grstearns", "billiamram", "deckycoss", "mariapacana", "tmcdemus", "marqs_m", "bglusman", "deanna_hood", "paulvstheworld", "gnclmorais", "gideondresdner", "swanpants", "lunacodess", "chimeracoder", "damiankao", "codee", "srmor", "linse", "buttsmeister", "KarenPunkPunk", "miriamlauter", "rowdyrabbit", "petefrance", "TedLee", "rawrjustin", "corydominguez", "chris_j_ryan", "vise890", "rodarmor", "tylersimko", "kanja", "rsnous", "nathanmarz", "webyrd", "jyli7", "gnitlis", "joystate"]
    #twitterHandleList = ["noelladsa", "anyharder"]
    update_twitter(twitterHandleList)


