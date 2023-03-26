"Generate a Map of ways traversed"
import logging
import time
import numpy as np

import geopandas as gpd
from shapely.geometry import Point

LOGGER_FORMAT = "[%(filename)s - %(funcName)s - %(levelname)s]: %(message)s"
logging.basicConfig(format=LOGGER_FORMAT)
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

class Explorer():
    """Loads in an activity database, an ROI, and calculates Explored_Ways. 
    Optionally - loads an Existing explorer DB (needed), and new 
    activities(filtered by last activity in explorer DB), and runs to find new ways"""
    SCHEMA = {
            'FID':'FID',
            'geometry':'GEOMETRY',
            'polylines':'GEOMETRY_POLYLINE',
            'traversals':'TRAVERSALS',
            'last_traversal': 'LAST_TRAVERSAL_DATE'
        }
    def __init__(self, roi, activity_db, point_buffer=1) -> None:
        # create points from point lines
        activities = self.parse_activity_data(activity_db)
        activity_points_raw_filtered = activities.cx[roi.roi_xmin:roi.roi_xmax, roi.roi_ymin:roi.roi_ymax]

        self.activity_points = activity_points_raw_filtered.to_crs(roi.approximate_crs)
        logger.debug('Total Points: %s', len(self.activity_points))
        self.activity_points['geometry'] = self.activity_points.geometry.buffer(point_buffer)
        # activity_points_buffered.to_file('points_test.shp')
        self.traversed_ways = None


    def parse_activity_data(self, activity_db) -> gpd.GeoDataFrame:
        # activity_coordinates = activity_db[['type', 'date', 'coordinates']].dropna()
        exploded_activity_points = activity_db.data.explode('coordinates')
        exploded_activity_points.dropna(subset=['coordinates'], inplace=True)
        exploded_activity_points['geometry'] = exploded_activity_points['coordinates'].apply(lambda x: Point(x[1],x[0]))
    
        activity_points_raw = gpd.GeoDataFrame(exploded_activity_points, geometry="geometry", crs="EPSG:4326")
        return activity_points_raw
        
    def find_traversed_ways(self, roi):
        # sjoin using ROI polygons
        tic = time.perf_counter()
        traversed_ways = roi.roi_ways.sjoin(self.activity_points, how="left")
        toc = time.perf_counter()
        logger.debug('Spatial Join took a total of %s seconds', round(toc-tic, 2))
        logger.debug("New GDF Columns: %s", ", ".join(traversed_ways.columns))
#         ##############
#         # get a count of traversals per way using groupby; could use more columns
#         # FID, geometry, polylines, index_right, "name", "date", "type", coordinates
# #         traversal_df = traversed_ways.groupby(["FID","name", "date", "type"]).count()
#         traversal_df = traversed_ways.groupby("FID").count()
#         #get latest traversal date
#         traversal_dates = traversed_ways.groupby('date')
#         print(traversal_df.columns)
#         ################

        traversal_groups = traversed_ways.groupby('FID')
        traversal_df = traversal_groups.agg({'FID': 'count',
                                            'date': np.max}
                                            )
        col_names = {
            'FID':'TRAVERSALS',
            'date': 'LAST_TRAVERSAL_DATE'
        }

        renamed_traversal_df = traversal_df.rename(columns=col_names)
        renamed_traversal_df['TRAVERSALS'] = renamed_traversal_df['TRAVERSALS'] - 1
#         print(renamed_traversal_df.sample(20))
        # merge results using the ROI ways
        traversal = roi.roi_ways.merge(renamed_traversal_df, 
                                                      how="left", 
                                                      on="FID")
#         print(traversal.sample(20))
        self.traversed_ways_gdf = gpd.GeoDataFrame(traversal, geometry="geometry",crs="epsg:32617")


        renamed = self.traversed_ways_gdf.rename(columns=self.SCHEMA)
        self.traversed_ways = renamed[list(self.SCHEMA.values())].fillna(0)
        logger.debug("Created traversed ways gdf with columns %s", ", ".join(self.traversed_ways.columns))
    def calcualte_coverage(self, coverage_dict=None):
        # convert to a save function to the Explored_Ways class
        cov = self.traversed_ways.astype(bool).sum(axis=0)
        total_ways = cov['FID']
        
        
        if coverage_dict:
            cov = {}
            for  key, value in coverage_dict.items():
                travs = self.traversed_ways[self.traversed_ways['Traversals'] <= value].astype(bool).sum(axis=0)
                cov[key] = travs / total_ways
    
            print(cov)
        else:
            cov = self.traversed_ways.astype(bool).sum(axis=0)
            coverage = cov['TRAVERSALS'] / cov['FID']
            print(f'Coverage: {coverage:.2%}')
            print(f'Ways Traversed: {cov["TRAVERSALS"]}')
        
    # def find_unmapped_activity_points(self,roi):
    #     tic = time.perf_counter()
    #     unmapped_activity_points = self.activity_points.sjoin(roi.roi_ways, how="left")
    #     toc = time.perf_counter()
    #     logger.debug('Spatial Join took a total of %s seconds', toc-tic)
    #     self.unmapped_activity_points = unmapped_activity_points.groupby(["name","type","date"]).count()
    def save(self, filename, geometry="Polyline"):
        if geometry == "Polyline":
            save_gdf = self.traversed_ways.drop(['GEOMETRY','LAST_TRAVERSAL_DATE'], axis=1)
            save_gdf.set_geometry('GEOMETRY_POLYLINE',inplace=True)
        else:
            save_gdf = self.traversed_ways.drop('GEOMETRY_POLYLINE', axis=1)
            logger.info(save_gdf.columns)

        save_gdf.to_file(filename)


class ROI():
    ROI_TYPES = ['file']
    def __init__(self, roi, roi_type, buffer=None) -> None:
        # determine loader based on roi type; assert
        if buffer:
            self.buffer = buffer
        else:
            self.buffer = 12
        
        if roi_type == 'file':
            raw_roi = self._import_roi_file(roi)
        else:
            pass

        self.roi_xmin, self.roi_ymin, self.roi_xmax, self.roi_ymax = raw_roi.total_bounds
        self.approximate_crs = raw_roi.geometry.estimate_utm_crs()
        logger.info('Found the following CRS from OSM Data: %s', self.approximate_crs)
        self.roi_ways = raw_roi.to_crs(self.approximate_crs)
        self.roi_ways['polylines'] = self.roi_ways['geometry']
        self.roi_ways['geometry'] = self.roi_ways.geometry.buffer(self.buffer, cap_style=2)

    def _import_roi_file(self, roi_file):
        logger.info('Loading ROI %s', roi_file)
        raw_roi_import = gpd.GeoDataFrame.from_file(roi_file)
        logger.debug('Loaded Shp file with headers: %s', ", ".join(raw_roi_import.columns))
        return raw_roi_import       # need to make debug loggin more verbose

class Explored_Ways():
    def __init__(self) -> None:
        self.created = "" # use now()
        
        self.total_way_count = 0
        self.explored_way_count = 0
        self.new_explore_way_count = 0
        
        self.total_way_length = 0
        self.explored_way_length = 0
        self.new_explored_way_length = 0
        
        
              
# output a percentage of coverage
# create better naming for columns names
# split out merge to separate func


# 3410 4274
# 4637 5377
# 5049 5727