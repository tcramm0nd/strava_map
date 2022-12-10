"Generate a Map of ways traversed"
import logging
import time

import geopandas as gpd
from shapely.geometry import Point

LOGGER_FORMAT = "[%(filename)s - %(funcName)s - %(levelname)s]: %(message)s"
logging.basicConfig(format=LOGGER_FORMAT)
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

class Explorer():
    def __init__(self, roi, activity_db, point_buffer=1) -> None:
        
        # create points from point lines
        activity_coordinates = activity_db['coordinates'].dropna()
        all_points = [item for sublist in activity_coordinates for item in sublist]
        shapely_points = []
        for coord in all_points:
            try:
                p = coord[1],coord[0]
                point = Point(p)
                shapely_points.append(point)
            except TypeError:
                logger.warning('No Points found!')
        activity_points_raw = gpd.GeoDataFrame(shapely_points, geometry=shapely_points, crs="EPSG:4326")
        activity_points_raw_filtered = activity_points_raw.cx[roi.roi_xmin:roi.roi_xmax, roi.roi_ymin:roi.roi_ymax]

        self.activity_points = activity_points_raw_filtered.to_crs(roi.approximate_crs)
        logger.debug('Total Points: %s', len(self.activity_points))
        self.activity_points['geometry'] = self.activity_points.geometry.buffer(point_buffer)
        # activity_points_buffered.to_file('points_test.shp')
    def find_traversed_ways(self, roi):
        tic = time.perf_counter()
        traversed_ways = roi.roi_ways.sjoin(self.activity_points, how="left")
        toc = time.perf_counter()
        logger.debug('Spatial Join took a total of %s seconds', toc-tic)
        self.traversed_ways = traversed_ways.groupby("FID").count()



class ROI():
    ROI_TYPES = ['file']
    def __init__(self, roi, roi_type, buffer=None) -> None:
        # determine loader based on roi type; assert
        if buffer:
            self.buffer = buffer
        else:
            self.buffer = 4
        
        if roi_type == 'file':
            raw_roi = self._import_roi_file(roi)
        else:
            pass

        self.roi_xmin, self.roi_ymin, self.roi_xmax, self.roi_ymax = raw_roi.total_bounds
        self.approximate_crs = raw_roi.geometry.estimate_utm_crs()
        logger.info('Found the following CRS from OSM Data: %s', self.approximate_crs)
        self.roi_ways = raw_roi.to_crs(self.approximate_crs)
        self.roi_ways['geometry'] = self.roi_ways.geometry.buffer(self.buffer, cap_style=2)
    def _import_roi_file(self, roi_file):
        logger.info('Loading %s', roi_file)
        raw_roi_import = gpd.GeoDataFrame.from_file(roi_file)
        logger.debug('Loaded Shp file as a %s', type(raw_roi_import))
        return raw_roi_import
    def update_traversal(self, traversal):
        self.traversed_roi_ways = self.roi_ways.merge(traversal, 
                                                      how="left", 
                                                      on="FID")

        # need to make debug loggin more verbose
        # need to figure out the correct spatial join, and why the geomety seems not to be saving
        # alternatively, inner join and then normal DB join back
      
        
# 3410 4274
# 4637 5377
# 5049 5727