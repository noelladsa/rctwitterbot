import twython
import sys
import json

api_key, api_secret, access_key, access_token = sys.argv[1:]

twy = twython.Twython(api_key,api_secret,access_key, access_token)
data = twy.get_user_timeline(screen_name="noelladsa", exclude_replies="true")

#with open('test.json') as data_file:    
 #   data = json.load(data_file)

def getTwitterText (twitterResponseDict):
    userTextList = []
    for tweet in twitterResponseDict:
         userTextList.append(tweet["text"])
    return  userTextList

print getTwitterText(data)  

