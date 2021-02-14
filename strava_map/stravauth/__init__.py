import json
import os.path
import urllib
import webbrowser
import requests
import datetime as dt
from loguru import logger


class Client():
    def __init__(self, client_id=None, client_secret=None):
        self.client_id = client_id
        self.client_secret = client_secret
        
        if os.path.isfile('.credentials.json'):
            self.read_creds()
            logger.debug('Loaded Credentials')
            if self.expires_at < dt.datetime.timestamp(dt.datetime.now()):
                self.refresh()
        # elif not (self.client_id or self.client_secret):
        else:
            self.authorize()
            
    def authorize(self):
        if not (self.client_id or self.client_secret):
            self.client_id = int(input('Enter Client ID: '))
            self.client_secret = input('Enter Client Secret: ')
            
        self.oauth_params = {"client_id": self.client_id,
                             "response_type": "code",
                             "redirect_uri": "http://localhost:8000/authorization_successful",
                             "scope": "read,profile:read_all,activity:read_all",
                             "approval_prompt": "force"
                             }

        url = 'https://www.strava.com/oauth/authorize?' + urllib.parse.urlencode(self.oauth_params)
        webbrowser.get().open(url)
        success_url = urllib.parse.urlparse(input('Paste the Success URL here:')).query
        query = urllib.parse.parse_qs(success_url)
        self.code = query['code']
        self.token_params = {"client_id": self.client_id,
                        "client_secret": self.client_secret,
                        "code": self.code,
                        "grant_type": "authorization_code"
                        }
        
        self.r = requests.post("https://www.strava.com/oauth/token", self.token_params)

        self.write_creds()

    def refresh(self):
    
        # if os.path.isfile('.credentials.json'):
        #     with open('.credentials.json') as f:
        #         credentials = json.load(f)
        #         logger.debug('Loaded Credentials')
        # else:
        #     self.authorize()
        #     logger.debug('Ran Authorization again')
            
        # self.client_id = credentials['client_id']
        # self.client_secret = credentials['client_secret']
        # self.refresh_token = credentials['refresh_token']
        self.refresh_params = {"client_id": self.client_id,
                        "client_secret": self.client_secret,
                        "grant_type": "refresh_token",
                        'refresh_token': self.refresh_token
                        }
        self.r = requests.post("https://www.strava.com/oauth/token", self.refresh_params)
        
        

        self.write_creds()
            
    def write_creds(self):
        
        self.credentials = self.r.json()
        self.access_token = self.credentials['access_token']

        self.credentials['client_id'] = self.client_id
        self.credentials['client_secret'] = self.client_secret

        with open('.credentials.json', 'w+') as f:
            json.dump(self.credentials, f)  
            
    def read_creds(self, path=None):
        if path:
            self.path = path
        else:
            self.path = '.credentials.json'
        
        with open(self.path) as f:
            self.credentials = json.load(f)
            self.client_id = int(self.credentials['client_id'])
            self.client_secret = str(self.credentials['client_secret'])
            self.access_token = self.credentials['access_token']
            self.refresh_token = self.credentials['refresh_token']
            self.expires_at = self.credentials['expires_at']
            
# if __name__ == '__main__':
#     Client()