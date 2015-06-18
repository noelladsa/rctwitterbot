from threading import Thread
import time
import requests
import twitter_interact


class TwitterWorker(Thread):
    a_token = None
    r_token = None

    @property
    def access_token(self):
        return self.a_token

    @access_token.setter
    def access_token(self, value):
        self.a_token = value

    @property
    def refresh_token(self):
        return self.r_token

    @refresh_token.setter
    def refresh_token(self, value):
        self.r_token = value

    def __init__(self, interval, key, secret, base_url, token_url):
        Thread.__init__(self)
        self.daemon = True
        self.recurser_list = []
        self.interval = interval
        self.consumer_key = key
        self.consumer_secret = secret
        self.base_url = base_url
        self.token_url = token_url

    def refresh_tokens(self):
        payload = {'grant_type': 'refresh_token',
                   'refresh_token': self.r_token}
        res = requests.post(self.token_url, data=payload)
        tokens_json = res.json()
        self.a_token = tokens_json["access_token"]
        self.r_token = tokens_json["refresh_token"]

    def run(self):
        while True:
            if self.a_token and self.r_token:
                print "Refreshing tokens, and updating list"
                self.refresh_tokens()
                self.update_list()
                twitter_interact.update_twitter(self.recurser_list)
                print "Sleeping..", self.interval
                break
            time.sleep(10)

    def get_api_endpoint(self, api_query):
        access_token_q = "?access_token="+self.access_token
        return self.base_url + api_query + access_token_q

    def update_list(self):
        batches = requests.get(self.get_api_endpoint('batches'))
        self.recurser_list = []
        for batch in batches.json():
            batch_people = 'batches/'+str(batch["id"])+'/people'
            people = requests.get(self.get_api_endpoint(batch_people))
            for person in people.json():
                self.recurser_list.append(person["twitter"])
        self.recurser_list = list(set(self.recurser_list))
        print self.recurser_list


if __name__ == "__main__":
    a = TwitterWorker(5)
    a.start()
    while True:
        pass
