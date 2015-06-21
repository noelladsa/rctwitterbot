from threading import Thread
import sys
import traceback
import time
import requests
import pickle
import os

import twitter_interact


class TwitterWorker(Thread):
    NAME = "TOKEN_FILE"

    def __init__(self, interval, base_url, token_url):
        Thread.__init__(self)
        self.daemon = True
        self.interval = interval
        self.base_url = base_url
        self.token_url = token_url
        self.a_token = None
        self.r_token = None
        self.load_tokens()

    def save_tokens(self, access_token, refresh_token):
        """Saves current token state to disk """
        self.a_token = access_token
        self.r_token = refresh_token
        pickle.dump((self.a_token, self.r_token), open(self.NAME, "wb"))

    def clear_tokens(self):
        self.save_tokens(None, None)

    def load_tokens(self):
        """ Loads previously used tokens """
        if not os.path.isfile(self.NAME):
            print "No Tokens were loaded, please login"
            return
        self.a_token, self.r_token = pickle.load(open(self.NAME, "rb"))

    def refresh_tokens(self):
        if not self.a_token and not self.r_token:
            return
        payload = {'grant_type': 'refresh_token',
                   'refresh_token': self.r_token}
        res = requests.post(self.token_url, data=payload)
        tokens = res.json()
        if "access_token" in tokens and "refresh_token" in tokens:
            self.save_tokens(tokens["access_token"], tokens["refresh_token"])
        else:
            self.clear_tokens()

    def run(self):
        while True:
            try:
                self.refresh_tokens()
                recursers = self.get_tweeting_recursers()
                twitter_interact.update_twitter(recursers)
            except:
                traceback.print_exc(file=sys.stdout)
            time.sleep(self.interval)

    def get_api_endpoint(self, api_query):
        access_token_q = "?access_token="+self.a_token
        return self.base_url + api_query + access_token_q

    def get_tweeting_recursers(self):
        if not self.a_token and not self.r_token:
            return
        batches = requests.get(self.get_api_endpoint('batches'))
        recurser_list = []
        for batch in batches.json():
            batch_people = 'batches/'+str(batch["id"])+'/people'
            people = requests.get(self.get_api_endpoint(batch_people))
            recurser_list += [person["twitter"] for person in people.json()
                              if person["twitter"]]
        return recurser_list


if __name__ == "__main__":
    base_url = 'https://www.recurse.com/api/v1/'
    access_token_url = 'https://www.recurse.com/oauth/token'
    a = TwitterWorker(10, base_url, access_token_url)
    a.start()
    while True:
        pass
