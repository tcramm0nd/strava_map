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
    Maybe an extension of activity DB?
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
        
        self.center = self._center_point()

        self.heatmap = folium.Map(location=self.center,
                tiles='Stamen Toner',
                zoom_start=14)
        
    def create_heatmap(self):
        """Creates a heatmap of Strava activity data
        Args:
            activities (str or list, optional): A string or list of activities
                to include in the heatmap. Defaults to 'All'.
        """        
                
        heatmap_coordinates = self.coordinates_by_type()
        gradients = self._generate_gradients()
        for a_type, coords in heatmap_coordinates.items():
            feature_group = folium.FeatureGroup(name=a_type, show=True)
            # if a_type in gradients.keys():
            #     gradient = gradients[a_type]
            # else:
            #     gradient = {0: 'white', 1: 'lawngreen'}
            gradient = gradients[a_type]
            feature_group.add_child(HeatMap(coords, radius=7, blur=5, gradient=gradient))
            self.heatmap.add_child(feature_group)
            
        self.heatmap.add_child(folium.map.LayerControl())
                
        filename = str(dt.date.today()) + str(self.activity_types) + '_activity_heatmap.html'
        self.heatmap.save(filename)
        webbrowser.open(filename)

    def coordinates_by_type(self):
        """Processes the coordinates for use.
        """     
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
        all_coords = self.data['coordinates'].apply(pd.Series).stack().reset_index(drop=True)            
        lat, lon = zip(*all_coords)
        center = [median(lat), median(lon)]
        return center

    def _generate_gradients(self):
        gradient_list = [{0: 'white', .9: 'blue', 1:'cyan'},
                         {0: 'white', .9: 'maroon', 1:'red'}
                         ]
        gradients = {}
        frequency = self.data.groupby('type').count()
        g_index = 0
        for i in frequency.index:
            if g_index <= len(gradient_list):
                gradients[i] = gradient_list[g_index]
                g_index +=1
            else:
                gradients[i] = {0:'white', 1:'black'}
        return gradients