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
    """A collection of Strava activity data.
    """    
    def __init__(self, activity_data):
        """Initializes a Map instance

        Args:
            activity_data (str, optional): Path to a saved activities.json file. Defaults to None.
        """        
        if activity_data:
            self._load = True
            self.activity_database = pd.read_json(activity_data)
        else:
            self._load = False
            self.get_activities()
            
        self._process_coordinates()
    
    def create_heatmap(self, activities='All'):
        """Creates a heatmap of Strava activity data

        Args:
            activities (str or list, optional): A string or list of activities
                to include in the heatmap. Defaults to 'All'.
        """        
        
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
        """Processes the coordinates for use.
        """        
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
        """Finds the center point of all activities
        """        
        all_coords = []
        for c in self.coords.values():
            all_coords.extend(c)
        coords = zip(*all_coords)
        self.center = []
        for c in coords:
            self.center.append(median(c))
                
    def _select_activities(self, activities):
        """Parses the input of activities

        Args:
            activities (str or list): A string or list of strings of activity types.

        Returns:
            list: A list of activities.
        """        
        if activities not in self.activity_types:
            activities = self.activity_types
        elif isinstance(activities, str):
            activities = [activities]
        else:
            pass
        
        return activities

    def save_activities(self, path=None):
        """Saves downloaded activity data as a JSON file

        Args:
            path (str, optional): Path to a directory to save activity data. Defaults to None.
        """
        
        filename = str(dt.date.today()) + '_strava_activities.json'
        if path:
            filename = path + filename
        self.activity_database.to_json(filename)
          
def convert_to_coords(map_data):
    """Decodes a Strava 'Summary Polyline' encoded for Google Maps.

    Args:
        map_data (dict): A dictionary containing a geo-data about a strava activity

    Returns:
        lsit: returns a list of coordinates: [lat,lon]
    """    
    encoded_polyline = map_data['summary_polyline']
    if encoded_polyline:
        decoded_polyline = polyline.decode(encoded_polyline)
        coords = [list(c) for c in decoded_polyline]
        return coords