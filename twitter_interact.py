import twython
import sys

api_key, api_secret, access_key, access_token = sys.argv[1:]

twy = twython.Twython(api_key,api_secret,access_key, access_token)
twitter.update_status(status="Blah")
