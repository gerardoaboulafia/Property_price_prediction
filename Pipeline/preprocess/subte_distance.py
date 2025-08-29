import geopy.distance
import geopandas as gpd
from shapely.geometry import Point
import pandas as pd

def calculate_subte_distance(data):
    df_subte = pd.read_csv('Pipeline/estaciones-de-subte copy.csv')
    geo_subte = gpd.GeoDataFrame(df_subte, geometry=gpd.points_from_xy(df_subte['long'], df_subte['lat']))

    gdf_clean = data.dropna(subset=['latitud', 'longitud'])
    gdf_clean['distancia_subte_cercano'] = gdf_clean.apply(lambda row: min(
        geo_subte['geometry'].apply(lambda station: geopy.distance.geodesic((row['latitud'], row['longitud']), (station.y, station.x)).km)
    ), axis=1)

    data = data.merge(gdf_clean[['distancia_subte_cercano']], left_index=True, right_index=True, how='left')
    return data
