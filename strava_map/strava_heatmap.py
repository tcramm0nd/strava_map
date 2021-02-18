import datetime as dt
import json
import urllib
import webbrowser
from statistics import median

import folium
import pandas as pd
import polyline
import requests
from folium.plugins import HeatMap

from . import stravauth

class Map():
    def __init__(self, activity_data=None):
        if activity_data:
            self._load = True
            self.activity_database = pd.read_json(activity_data)
        else:
            self._load = False
            self.get_activities()
            
        self._process_coordinates()
           
    def get_activities(self):

        self.client = stravauth.Client()
        page = 1
        url = 'https://www.strava.com/api/v3/athlete/activities?'
        activity_list = []
        while True:
            activity_params = {'access_token': self.client.access_token,
                    'per_page': '100',
                    'page': page}
            r = requests.get(url + urllib.parse.urlencode(activity_params))
            if r.status_code != 200: 
                print('Refreshing token')
                self.client.refresh()
                activity_params = {'access_token': self.client.access_token,
                    'per_page': '100',
                    'page': page}
                r = requests.get(url + urllib.parse.urlencode(activity_params))
            activities = r.json()
            activity_list.extend(activities)

            if len(activities) < 100:
                break

            page += 1
            
        print(f'Retrieved {len(activity_list)} total activities')
        self.activity_database = pd.DataFrame(activity_list)      
        
    def create_heatmap(self, activities='All'):
        
        activities = self._select_activities(activities)

        gradients = {'Run':{0: 'white', .9: 'blue', 1:'cyan'},
                    'Ride': {0: 'white', .9: 'maroon', 1:'red'}
                    }
        self._center_point()
        self.heatmap = folium.Map(location=self.center,
                        tiles='Stamen Toner',
                        zoom_start=14
            )
        for a in activities:
            feature_group = folium.FeatureGroup(name=a, show=True)
            if a in ['Ride', 'Run']:
                gradient = gradients[a]
            else:
                gradient = {0: 'white', 1: 'lawngreen'}
            feature_group.add_child(HeatMap(self.coords[a], radius=7, blur=5, gradient=gradient))
            self.heatmap.add_child(feature_group)
            
        self.heatmap.add_child(folium.map.LayerControl())
                
        filename = str(dt.date.today()) + '_activity_heatmap.html'
        self.heatmap.save(filename)
        webbrowser.open(filename)

    def _process_coordinates(self):
        # Decode summary Polyline
        if self._load == False:
            self.activity_database['coords'] = self.activity_database['map'].apply(
                lambda x: convert_to_coords(x))
        # Find the centerpoint of all activity data
        #
        activity_types = pd.unique(self.activity_database['type'])
        self.coords = {}
        for t in activity_types:
            a = self.activity_database[self.activity_database['type'] == t]
            c = a['coords'].apply(pd.Series).stack().reset_index(drop=True)
            if len(c) > 0:
                self.coords[t] = c
        self.activity_types = self.coords.keys()
    
    def _center_point(self):
        all_coords = []
        for c in self.coords.values():
            all_coords.extend(c)
        coords = zip(*all_coords)
        self.center = []
        for c in coords:
            self.center.append(median(c))
                
    def _select_activities(self, activities):
        if activities not in self.activity_types:
            activities = self.activity_types
        elif isinstance(activities, str):
            activities = [activities]
        else:
            pass
        
        return activities

    def save_activities(self, path=None):
        if not path:
            filename = str(dt.date.today()) + '_strava_activities.json'
            self.activity_database.to_json(filename)  
          
def convert_to_coords(map_data):

    encoded_polyline = map_data['summary_polyline']
    if encoded_polyline:
        decoded_polyline = polyline.decode(encoded_polyline)
        coords = [list(c) for c in decoded_polyline]
        return coords