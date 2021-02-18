import datetime as dt
import json
import os.path
import urllib
import webbrowser

import requests
from loguru import logger


class Client():
    """Creates a Strava API Client
    """
    def __init__(self, client_id=None, client_secret=None):
        self.client_id = client_id
        self.client_secret = client_secret
        
        if os.path.isfile('.credentials.json'):
            self.read_creds()
            logger.debug('Loaded Credentials')
            if self.expires_at < dt.datetime.timestamp(dt.datetime.now()):
                self.refresh()
        else:
            self.authorize()
            
    def authorize(self, response_type='code',
                  scope='read,profile:read_all,activity:read_all',
                  approval_prompt='auto'
                  ):
        """Authorizes the Strava Client if there are no exisiting credentials.

        Args:
            response_type (str, optional): The response of the authorization
                request. Defaults to 'code'.
            scope (str, optional): The scope of what the app is allowed to
                access. Defaults to 'read,profile:read_all,activity:read_all'.
            approval_prompt (str, optional): Option to either force the user to
                acknowledge the request, or automaticaly pass through if the app
                is already authorized. Defaults to 'auto'.
        """
        if not (self.client_id or self.client_secret):
            self.client_id = int(input('Enter Client ID: '))
            self.client_secret = input('Enter Client Secret: ')
            
        self.oauth_params = {"client_id": self.client_id,
                             "response_type": response_type,
                             "redirect_uri": "http://localhost:8000/authorization_successful",
                             "scope": scope,
                             "approval_prompt": approval_prompt
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
        """Refreshes the Bearer Token if the token has expired
        """
        if self.access_token:
            del self.access_token
        self.refresh_params = {"client_id": self.client_id,
                        "client_secret": self.client_secret,
                        "grant_type": "refresh_token",
                        'refresh_token': self.refresh_token
                        }
        self.r = requests.post("https://www.strava.com/oauth/token", self.refresh_params)
        self.write_creds()
            
    def write_creds(self):
        """Writes Strava authorization info to a credentials JSON
        """
        self.credentials = self.r.json()
        self.access_token = self.credentials['access_token']

        self.credentials['client_id'] = self.client_id
        self.credentials['client_secret'] = self.client_secret

        with open('.credentials.json', 'w+') as f:
            json.dump(self.credentials, f)
            
    def read_creds(self, path=None):
        """Reads Strava Credentials from an existing credentials file.

        Args:
            path (str, optional): Path to an existing credentials file. Defaults to None.
        """
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