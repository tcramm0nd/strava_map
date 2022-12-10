import datetime as dt
import logging
import urllib

import pandas as pd
import polyline
import requests

from . import stravauth

LOGGER_FORMAT = "[%(filename)s - %(funcName)s - %(levelname)s]: %(message)s"
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

class ActivityDB():
    def __init__(self, data=None, fetch=False, filename=None, client_id=None, client_secret=None):
        """Sets up an Activity DB.

        Args:
            data (dict, optional): Dictionary of existing Strave Data. Defaults to None.
            fetch (bool, optional): Whether to fetch activities on initialization. Defaults to False.
            filename (str, optional): File to read Activity Data from. Defaults to None.
            client_id (str, optional): Strava Client ID. Defaults to None.
            client_secret (str, optional): Strava Client Secret. Defaults to None.
        """

        if data:
            self._data = pd.DataFrame(data)
        elif fetch:
            self._data = pd.DataFrame(self.fetch(client_id=client_id, client_secret=client_secret))
        elif filename:
            self._data = pd.read_json(filename)
        else:
            self._data = pd.DataFrame()

        if not self._data.empty:
            if 'coordinates' not in self._data.columns and 'map' in self._data.columns:
                self._data['coordinates'] = self._data['map'].apply(
                    lambda x: convert_to_coords(x))        
            if 'date' not in self._data.columns:
                self._data['date'] = self._data['start_date'].str.extract(r'(\d{4}-\d{2}-\d{2})')
            self.data = self._data[['name', 'date', 'type', 'coordinates']]

    def fetch(self, activity_id=None, per_page=100, include_all_efforts=True,
              client_id=None, client_secret=None):
        """Fetches Activity data from Strava.

        Args:
            activity_id (int, optional): ID for a specific activity. Defaults to None.
            per_page (int, optional): number of records per page. Defaults to 100.
            include_all_efforts (bool, optional): Whether or not to include all activity. Defaults to True.
            client_id (str, optional): Client ID. Defaults to None.
            client_secret (str, optional): Client Secret. Defaults to None.

        Returns:
            dict: JSON of activities.
        """
        self.client = stravauth.Client(client_id=client_id, client_secret=client_secret)

        if activity_id:
            activity_params = {'access_token': self.client.access_token,
                               'include_all_efforts': include_all_efforts}
            url = f'https://www.strava.com/api/v3/activities/{activity_id}?'
            return self._responder(url, activity_params)
        else:
            page = 1
            per_page = per_page
            activity_params = {'access_token': self.client.access_token,
                            'per_page': per_page,
                            'page': page
                            }
            url = 'https://www.strava.com/api/v3/athlete/activities?'
            activity_list = []
            while True:
                activities = self._responder(url, activity_params)
                activity_list.extend(activities)

                if len(activities) < per_page:
                    break

                page += 1
                activity_params['page'] = page

            print(f'Retrieved {len(activity_list)} total activities')

            return activity_list

    def _responder(self, url, params):
        """Helper to get JSON.

        Args:
            url (str): url to fetch
            params (dict): dictionary with payload to pass

        Raises:
            PermissionError: Error if authentification is bad.

        Returns:
            dict: JSON response
        """

        r = requests.get(url + urllib.parse.urlencode(params))
        if r.ok:
            return r.json()
        else:
            try:
                self.client.refresh()
                params['access_token'] = self.client.access_token
                r = requests.get(url + urllib.parse.urlencode(params))
                return r.json()
            except:
                raise PermissionError

    def save(self, path=None, filename=None):
        """Saves the Activity DB

        Args:
            path (str, optional): Location to save the file. Defaults to None.
            filename (str, optional): File name for saved DB. Defaults to None.
        """
        if not filename:
            filename = str(dt.date.today()) + '_strava_activities.json'
        if path:
            filename = path + filename

        self.data.to_json(filename)
    def __getitem__(self, key):
        return self._data[key]
        

def convert_to_coords(map_data):
    """Converts Encoded Polyline to coordinates

    Args:
        map_data (dict): Dictionary of Activity Data.

    Returns:
        list: Decoded polyline as coordinates list.
    """

    encoded_polyline = map_data['summary_polyline']
    if encoded_polyline:
        decoded_polyline = polyline.decode(encoded_polyline)
        return decoded_polyline
