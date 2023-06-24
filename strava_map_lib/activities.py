"Tools for Activities"
import datetime as dt
import logging
from urllib.parse import urlencode
from typing import Optional, Union

import pandas as pd
import polyline
import requests

from . import stravauth

LOGGER_FORMAT = "[%(filename)s - %(funcName)s - %(levelname)s]: %(message)s"
logging.basicConfig(format=LOGGER_FORMAT)
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


class ActivityDB():
    """Database for holding activities
    """

    def __init__(self, data: Optional[dict] = None, fetch: bool = False, filename: Optional[str] = None, client_id: Optional[str] = None, client_secret: Optional[str] = None) -> None:
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
            self._data = pd.DataFrame(self.fetch(
                client_id=client_id, client_secret=client_secret))
        elif filename:
            logger.info('Loading Activity files %s', filename)
            self._data = pd.read_json(filename)
        else:
            self._data = pd.DataFrame()

        if not self._data.empty:
            if 'coordinates' not in self._data.columns and 'map' in self._data.columns:
                self._data['coordinates'] = self._data['map'].apply(
                    lambda x: self.convert_to_coords(x))
            if 'date' not in self._data.columns:
                self._data['date'] = self._data['start_date'].str.extract(
                    r'(\d{4}-\d{2}-\d{2})')
            # should make this configurable!
            self.data = self._data[['name', 'date', 'type', 'coordinates']]

    @classmethod
    def from_file(cls, filename: str):
        return pd.read_json(filename)
    
    def fetch(self, activity_id: Optional[int] = None, per_page: int = 100, include_all_efforts: bool = True,
              client_id: Optional[str] = None, client_secret: Optional[str] = None) -> Union[list, dict]:
        """Fetches Activity data from Strava.

        Args:
            activity_id (int, optional): ID for a specific activity. Defaults to None.
            per_page (int, optional): number of records per page. Defaults to 100.
            include_all_efforts (bool, optional): Whether or not to include all activity. Defaults to True.
            client_id (str, optional): Client ID. Defaults to None.
            client_secret (str, optional): Client Secret. Defaults to None.

        Returns:
            list: JSON of activities.
        """
        logger.debug('Initializing stravauth client')
        self.client = stravauth.Client(
            client_id=client_id, client_secret=client_secret)

        if activity_id:
            activity_params = {'access_token': self.client.access_token,
                               'include_all_efforts': include_all_efforts}
            url = f'https://www.strava.com/api/v3/activities/{activity_id}?'
            return self._responder(url, activity_params)
        else:
            page = 1
            activity_params = {'access_token': self.client.access_token,
                               'per_page': per_page,
                               'page': page
                               }
            url = 'https://www.strava.com/api/v3/athlete/activities?'
            activity_list = []
            while True:
                logger.debug("Fetching page %s of activities", page)
                activities = self._responder(url, activity_params)
                activity_list.extend(activities)

                if len(activities) < per_page:
                    break

                page += 1
                activity_params['page'] = page

            print(f'Retrieved {len(activity_list)} total activities')

            return activity_list

    def _responder(self, url: str, params: dict) -> dict:
        """Helper to get JSON.

        Args:
            url (str): url to fetch
            params (dict): dictionary with payload to pass

        Raises:
            PermissionError: Error if authentification is bad.

        Returns:
            dict: JSON response
        """

        resp = requests.get(url + urlencode(params), timeout=5)
        if resp.ok:
            return resp.json()
        else:
            try:
                self.client.refresh()
                params['access_token'] = self.client.access_token
                resp = requests.get(url + urlencode(params), timeout=5)
                return resp.json()
            except Exception as error:
                raise PermissionError(error) from error

    def save(self, path: Optional[str] = None, filename: Optional[str] = None):
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

    def __getitem__(self, key: str):
        return self._data[key]

    @staticmethod
    def convert_to_coords(map_data: dict) -> list:
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
        else:
            return []
