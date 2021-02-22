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
    def __init__(self, activity_db, activity_types='All', split_by_type=True, start_date=None,
                 end_date=None, heatmap=True, kml=False):
         
        self.data = activity_db.data
        
        # set the activity types
        if activity_types == 'All':
            self.activity_types = pd.unique(self.data['type'])
        elif isinstance(activity_types, str):
            self.activity_types = [activity_types]
        else:
            self.activity_types = activity_types
        
        self._split = split_by_type
        self.start_date = start_date
        self.end_date = end_date

        
        self.center = self._center_point()
   
        if activity_data:
            self._load = True
            self.activity_database = pd.read_json(activity_data)
        else:
            self.activity_types = activity_types
        
        self._split = split_by_type
        
        self.center = self._center_point()

        self.heatmap = folium.Map(location=self.center,
                tiles='Stamen Toner',
                zoom_start=14)
        
    def create_heatmap(self):     
        
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
        heatmap_coordinates = self.coordinates_by_type()
        gradients = self._generate_gradients()
        for a_type, coords in heatmap_coordinates.items():
            feature_group = folium.FeatureGroup(name=a_type, show=True)
            gradient = gradients[a_type]
            feature_group.add_child(HeatMap(coords, radius=7, blur=5, gradient=gradient))
            self.heatmap.add_child(feature_group)
            
        self.heatmap.add_child(folium.map.LayerControl())
                
        filename = str(dt.date.today()) + str(self.activity_types) + '_activity_heatmap.html'
        self.heatmap.save(filename)
        webbrowser.open(filename)

    def coordinates_by_type(self):
      
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
 
        if self._split:     
            coords = {}
            for t in self.activity_types:
                a = self.data[self.data['type'] == t]
                c = a['coordinates'].apply(pd.Series).stack().reset_index(drop=True)
                if len(c) > 0:
                    coords[t] = c
        else:
            coords = {'All': self.data.apply(pd.Series).stack().reset_index(drop=True)}
        return coords
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
    def _generate_gradients(self):
        gradient_list = [{0: 'white', .9: 'blue', 1:'cyan'},
                         {0: 'white', .9: 'maroon', 1:'red'}
                         ]
        gradients = {}
        frequency = self.data['type'].value_counts()#.sort_values(['type'], ascending=False)
        logger.debug(frequency.head())
        logger.debug(frequency.index)
        g_index = 0
        for i in frequency.index:
            if g_index < len(gradient_list):
                gradients[i] = gradient_list[g_index]
                g_index +=1
            else:
                gradients[i] = {0:'white', 1:'black'}
        return gradients
