# +
import re
import requests
import censusdata
import requests
import pandas as pd
import numpy as np
import ast
import time
import os
import json
from shapely.geometry import Point
from shapely.geometry.polygon import Polygon
from geopandas import *

import warnings
warnings.filterwarnings('ignore')
# -

# import census tract features
df_census_tract_all = pd.read_excel('census_data/wi_tract_feature_file.xlsx', converters={'geoid_tract':str})


def get_census_df(df_hs):

    # create df of census features for all tracts across all Madison counties
    with open('census_data/tract_shape/tl_2020_55_all.json') as f:
        tract_geo_wi = json.load(f)

    n = len(tract_geo_wi['features'])
    geo_ids = np.array([tract_geo_wi['features'][i]['properties']['GEOID10'] for i in range(n)])

    tract_polys = []
    for i in range(n):
        poly_inp = tract_geo_wi['features'][i]['geometry']['coordinates'][0]
        if type(poly_inp[0][0]) == list:
            poly_inp = tract_geo_wi['features'][i]['geometry']['coordinates'][0][0]
        polygon = Polygon(poly_inp)
        tract_polys.append(polygon)

    # spatial join for address census tract columns 
    geo_col = []
    for i in range(len(df_hs)):
        lat = df_hs['lats'].values[i]
        long = df_hs['longs'].values[i]
        point = Point(long, lat)
        geo_col.append(point)
    df_hs['point'] = geo_col

    tract_df = pd.DataFrame()
    tract_df['geoid_tract'] = geo_ids
    tract_df['tract_poly'] = tract_polys

    # join on tract census features
    hs_gdf = GeoDataFrame(df_hs, crs="EPSG:4326", geometry='point')
    tract_gdf = GeoDataFrame(tract_df, crs="EPSG:4326", geometry='tract_poly')
    df_hs_join = geopandas.sjoin(tract_gdf, hs_gdf, how="right", op='contains')
    
    # handle overlapping census tracts
    df_hs_join = df_hs_join.drop_duplicates(subset=['level_0'])
    df_hs_join.reset_index(drop=True, inplace=True)

    # final join
    df = df_hs_join.join(df_census_tract_all.set_index('geoid_tract'), on = 'geoid_tract')
    df = df.drop(['index_left', 'geoid_tract', 'point'], axis = 1)

    return df
