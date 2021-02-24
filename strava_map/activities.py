import datetime as dt
import urllib

import pandas as pd
import polyline
import requests

from . import stravauth

class ActivityDB():
    def __init__(self, data=None, fetch=False, filename=None,
                 client_id=None, client_secret=None):
        
        # Initialize the Strava Client
        self.client = stravauth.Client(client_id=client_id, client_secret=client_secret)

        if data:
            self._data = pd.DataFrame(data)
        elif fetch:
            self._data = pd.DataFrame(self.fetch())
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
    
    def fetch(self, activity_id=None, per_page=100, include_all_efforts=True):
        if activity_id:
            activity_params = {'access_token': self.client.access_token,
                               'include_all_efforts': include_all_efforts}
            
            url = f'https://www.strava.com/api/v3/activities/{activity_id}?'
            
            # r = requests.get(url + urllib.parse.urlencode(activity_params))
            # if r.ok:
            #     return r.json()
            # else:
            #     print(f'Retrieval Failed:{r.status_code}, \n{r.json()}')
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
                # r = requests.get(url + urllib.parse.urlencode(activity_params))
                # if not r.ok:
                #     try:
                #         self.client.refresh()
                #         activity_params['access_token'] = self.client.access_token
                #         r = requests.get(url + urllib.parse.urlencode(activity_params))
                #     except:
                #         raise PermissionError
                    
                activities = self._responder(url, activity_params)
                activity_list.extend(activities)

                if len(activities) < per_page:
                    break

                page += 1
                activity_params['page'] = page
                
            print(f'Retrieved {len(activity_list)} total activities')
            
            return activity_list

    def _responder(self, url, params):            
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
        """Saves downloaded activity data as a JSON file
        Args:
            filename (str, optional): Path to a directory to save activity data. Defaults to None.
        """
        if not filename:
            filename = str(dt.date.today()) + '_strava_activities.json'
            
        if path:
            filename = path + filename

        self.data.to_json(filename)
        

def convert_to_coords(map_data):
    encoded_polyline = map_data['summary_polyline']
    if encoded_polyline:
        decoded_polyline = polyline.decode(encoded_polyline)
        return decoded_polyline

