"Creates a heatmap"
import datetime as dt
import logging
import webbrowser
from statistics import median

import folium
import pandas as pd
import simplekml
from folium.plugins import HeatMap

LOGGER_FORMAT = "[%(filename)s - %(funcName)s - %(levelname)s]: %(message)s"
logging.basicConfig(format=LOGGER_FORMAT)
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

class Map():
    def __init__(self, activity_db, activity_types='All', split_by_type=True):
        # , start_date=None,
                #  end_date=None, heatmap=True, kml=False
        """Creates a Map of the Activity Data.

        Args:
            activity_db (ActivityDB): A strava_map ActivityDB
            activity_types (str, optional): Activity types to include. Defaults to 'All'.
            split_by_type (bool, optional): Whether to split activities by type. Defaults to True.
            start_date (DateTime, optional): Start Date filter. Defaults to None.
            end_date (DateTime, optional): End Date Filter. Defaults to None.
            heatmap (bool, optional): Whether to generate a Heat Map. Defaults to True.
            kml (bool, optional): Whether to generate a KML. Defaults to False.
        """

        self.data = activity_db.data
        self.data.dropna(subset=['coordinates'], inplace=True)
        # try the *[] syntax to simplify this
        _all_activity_types = set(pd.unique(self.data['type']))
        if isinstance(activity_types, str):
            activity_types = [activity_types]

        if set(activity_types).issubset(_all_activity_types):
            self.activity_types = activity_types
            self.activity_str = "_".join(self.activity_types)
        else:
            self.activity_types = _all_activity_types
            self.activity_str = 'All'

        self._split = split_by_type

        self.center = self._center_point()

        self.heatmap = folium.Map(location=self.center,
                tiles='Stamen Toner',
                zoom_start=14)

    def create_heatmap(self):
        """Create a Heatmap of Activities.
        """

        heatmap_coordinates = self._coordinates_by_type()
        gradients = self._generate_gradients()
        for a_type, coords in heatmap_coordinates.items():
            feature_group = folium.FeatureGroup(name=a_type, show=True)
            gradient = gradients[a_type]
            feature_group.add_child(HeatMap(coords, radius=7, blur=5, gradient=gradient))
            self.heatmap.add_child(feature_group)

        self.heatmap.add_child(folium.map.LayerControl())

        filename = "_".join([str(dt.date.today()),
                            self.activity_str,
                            'activities.html'])
        self.heatmap.save(filename)
        webbrowser.open(filename)

    def create_kml(self):
        """Create a KML of Activity Data.
        """

        kml = simplekml.Kml(open=1)
        for _, activity in self.data.iterrows():
            coords = [tuple(reversed(c)) for c in activity['coordinates']]
            kml.newlinestring(name=activity['name'], coords=coords)

        filename = "_".join([str(dt.date.today()),
                            self.activity_str,
                            'activities.kml'])

        kml.save(filename)

    def _coordinates_by_type(self):
        """Processes coordinates by type

        Returns:
            list: list of coords
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
        """Generate the map center point.

        Returns:
            list: coordinates
        """

        all_coords = self.data['coordinates'].apply(pd.Series).stack().reset_index(drop=True)
        lat, lon = zip(*all_coords)
        center = [median(lat), median(lon)]
        return center

    def _generate_gradients(self):
        """Creates the Grradients for each activity.

        Returns:
            dict: Dictionary with gradient definitions
        """

        gradient_list = [{0: 'white', .9: 'blue', 1:'cyan'},
                         {0: 'white', .9: 'maroon', 1:'red'}
                         ]
        gradients = {}
        frequency = self.data['type'].value_counts()
        g_index = 0
        for i in frequency.index:
            if g_index < len(gradient_list):
                gradients[i] = gradient_list[g_index]
                g_index +=1
            else:
                gradients[i] = {0:'white', 1:'black'}
        return gradients

    def _file_namer(self, file_type):
        """Helper for file naming

        Args:
            file_type (str): Defines the type of file.

        Returns:
            str: file name
        """

        date = str(dt.date.today())
        activities = "_".join(self.activity_types)
        return "_".join([date,activities, file_type])
