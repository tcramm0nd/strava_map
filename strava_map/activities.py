from . import stravauth
import requests
import urllib
import json
import pandas as pd
import polyline
import datetime as dt

class ActivityDB():
    def __init__(self, data=None, fetch=False, filename=None):
        if data:
            self._data = pd.DataFrame(data)
        elif fetch:
            self._data = pd.DataFram(self.fetch())
        elif filename:
            self._data = pd.read_json(filename)
        else:

            self.data = pd.DataFrame()

            self._data = pd.DataFrame()

        if not self._data.empty:
            if 'coordinates' not in self._data.columns:
                self._data['coordinates'] = self._data['map'].apply(
                    lambda x: self._convert_to_coords(x)) 
            
            if 'date' not in self._data.columns:
                self._data['date'] = self._data['start_date'].str.extract(r'(\d{4}-\d{2}-\d{2})')
                
            self.data = self._data[['name', 'date', 'type', 'coordinates']]
            self._data.dropna(subset=['coordinates'])

            self._data = pd.DataFrame()
            
        if not self._data.empty:
            if 'coordinates' not in self._data.columns and 'map' in self._data.columns:
                self._data['coordinates'] = self._data['map'].apply(
                    lambda x: self._convert_to_coords(x)) 
            
            self._data.dropna(subset=['coordinates'])
        
            if 'date' not in self._data.columns:
                self._data['date'] = self._data['start_date'].str.extract(r'(\d{4}-\d{2}-\d{2})')
            self.data = self._data[['name', 'date', 'type', 'coordinates']]
    
    def fetch(self, client_id=None, client_secret=None, per_page=100):
        client = stravauth.Client(client_id=client_id, client_secret=client_secret)
        page = 1
        per_page = per_page
        activity_params = {'access_token': client.access_token,
                           'per_page': per_page,
                           'page': page
                           }
        url = 'https://www.strava.com/api/v3/athlete/activities?'
        activity_list = []
        while True:
            r = requests.get(url + urllib.parse.urlencode(activity_params))
            if r.status_code != 200: 
                print('Refreshing token')
                client.refresh()
                activity_params['access_token'] = client.access_token
                r = requests.get(url + urllib.parse.urlencode(activity_params))
            activities = r.json()
            activity_list.extend(activities)

            if len(activities) < per_page:
                break

            page += 1
            activity_params['page'] = page
            
        print(f'Retrieved {len(activity_list)} total activities')
        
        return activity_list

    def _convert_to_coords(self, map_data):
        encoded_polyline = map_data['summary_polyline']
        if encoded_polyline:
            decoded_polyline = polyline.decode(encoded_polyline)
            coords = [list(c) for c in decoded_polyline]
            return coords
    def save(self, path=None, filename=None):
        """Saves downloaded activity data as a JSON file

        Args:
            filename (str, optional): Path to a directory to save activity data. Defaults to None.
        """
        if not filename:
            filename = str(dt.date.today()) + '_strava_activities.json'
            
        if path:
            filename = path + filename

        self.data.to_json(filename)