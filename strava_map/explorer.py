import logging
from shapely.geometry import Point

import geopandas as gpd

from strava_map import ActivityDB

LOGGER_FORMAT = "[%(filename)s:%(lineno)s - %(funcName)s - %(levelname)s]: %(message)s"
logging.basicConfig(format=LOGGER_FORMAT)
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

class Explorer():
    def __init__(self, file_name, activity_db) -> None:
        logger.debug('Loading %s', file_name)
        split_ways_raw = gpd.GeoDataFrame.from_file(file_name)
        xmin, ymin, xmax, ymax = split_ways_raw.total_bounds
        # geom = split_ways_raw['geometry']
        # geom.to_file('split_ways.shp')
        logger.debug('GDF Head:\n%s', split_ways_raw.head())
        self.approximate_crs = split_ways_raw.geometry.estimate_utm_crs()
        logger.debug('Found the following CRS from OSM Data: %s', self.approximate_crs)
        split_ways = split_ways_raw.to_crs(self.approximate_crs)
        logger.debug('GDF Head:\n%s', split_ways.head())

        # geom = split_ways_raw['geometry']
        # geom.to_file('split_ways_32617.shp')
        buffered_ways = split_ways.buffer(4, cap_style=2)
        # buffered_ways.to_file('buffered_ways.shp')
        
        # create points from point lines
        all_points = activity_db._data['coordinates']
        logger.debug(all_points)
        shapely_points = []
        for point_list in all_points:
            try:
                logger.debug('Loading %s points', len(point_list))

                for p in point_list:
                    p = p[1],p[0]
                    point = Point(p)
                    shapely_points.append(point)
            except TypeError:
                logger.warning('No Points found!')
        activity_points_raw = gpd.GeoSeries(shapely_points, crs="EPSG:4326")
        activity_points_raw_filtered = activity_points_raw.cx[xmin:xmax, ymin:ymax]
        
        activity_points = activity_points_raw_filtered.to_crs(self.approximate_crs)
        logger.debug('Total Points: %s', len(activity_points))
        logger.debug('Points GDF Head:\n%s', activity_points.sample(5))
        activity_points_buffered = activity_points.buffer(1.5)
        # activity_points_buffered.to_file('points_test.shp')
      
        
# 3410 4274
# 4637 5377
# 5049 5727