""" Makes a map of paths one has traversed"""
import logging
import geopandas as gpd

logging.basicConfig(format='%(name)s-%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
# import shp of ways from shp file (eventually write an osm API that will retrieve and split)
# buffer into a reasonable distance - add column for this geom // plot this somehow
q = gpd.GeoDataFrame.from_file('')
q.buffer(0.2)
# fetch Strava data
# calculate number of points within polys for each segment
# column for 'traveled'
# plot results



