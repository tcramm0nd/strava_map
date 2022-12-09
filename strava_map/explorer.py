"Generate a Map of ways traversed"
import logging

import geopandas as gpd
from shapely.geometry import Point

LOGGER_FORMAT = "[%(filename)s:%(lineno)s - %(funcName)s - %(levelname)s]: %(message)s"
logging.basicConfig(format=LOGGER_FORMAT)
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

class Explorer():
    def __init__(self, roi, activity_db, point_buffer=1) -> None:
        
        # create points from point lines
        activity_coordinates = activity_db._data['coordinates'].dropna()
        all_points = [item for sublist in activity_coordinates for item in sublist]
        shapely_points = []
        for coord in all_points:
            try:
                p = coord[1],coord[0]
                point = Point(p)
                shapely_points.append(point)
            except TypeError:
                logger.warning('No Points found!')
        activity_points_raw = gpd.GeoSeries(shapely_points, crs="EPSG:4326")
        activity_points_raw_filtered = activity_points_raw.cx[roi.roi_xmin:roi.roi_xmax, roi.roi_ymin:roi.roi_ymax]

        activity_points = activity_points_raw_filtered.to_crs(roi.approximate_crs)
        logger.debug('Total Points: %s', len(activity_points))
        logger.debug('Points GDF Head:\n%s', activity_points.sample(5))
        self.activity_points = activity_points.buffer(point_buffer)
        # activity_points_buffered.to_file('points_test.shp')
        



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
        logger.debug('GDF Head:\n%s', raw_roi.head())
        self.approximate_crs = raw_roi.geometry.estimate_utm_crs()
        logger.debug('Found the following CRS from OSM Data: %s', self.approximate_crs)
        roi = raw_roi.to_crs(self.approximate_crs)
        logger.debug('GDF Head:\n%s', roi.head())
        self.roi_ways = roi.buffer(self.buffer, cap_style=2)   
    def _import_roi_file(self, roi_file):
        logger.info('Loading %s', roi_file)
        raw_roi_import = gpd.GeoDataFrame.from_file(roi_file)
        return raw_roi_import

     
        
      
        
# 3410 4274
# 4637 5377
# 5049 5727