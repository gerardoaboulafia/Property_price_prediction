import geopy.distance
import geopandas as gpd
from shapely.geometry import Point
import pandas as pd
import numpy as np

def calculate_subte_distance(data: pd.DataFrame, estaciones_csv_path: str) -> pd.DataFrame:
    df = data.copy()
    if 'flag' not in df.columns:
        df['flag'] = None
    
    subte = pd.read_csv(estaciones_csv_path)
    
    if 'long' in subte.columns and 'lon' not in subte.columns:
        subte = subte.rename(columns={'long': 'lon'})
    
    if not {'lat', 'lon'}.issubset(subte.columns):
        raise ValueError("El CSV de estaciones debe tener columnas 'lat' y 'lon'.")
    
    mask_ok = df['flag'].isna() & df[['lat', 'lon']].notna().all(axis=1)
    
    if 'distancia_subte_cercano' not in df.columns:
        df['distancia_subte_cercano'] = np.nan
    
    if mask_ok.any():
        from sklearn.neighbors import BallTree
        
        R = 6371.0088  # Earth radius in km
        
        stations_rad = np.deg2rad(subte[['lat', 'lon']].to_numpy())
        points_rad = np.deg2rad(df.loc[mask_ok, ['lat', 'lon']].to_numpy())
        
        tree = BallTree(stations_rad, metric='haversine')
        dists_rad, _ = tree.query(points_rad, k=1)  # Fixed: points*rad -> points_rad
        
        df.loc[mask_ok, 'distancia_subte_cercano'] = (dists_rad.flatten() * R)
    
    return df