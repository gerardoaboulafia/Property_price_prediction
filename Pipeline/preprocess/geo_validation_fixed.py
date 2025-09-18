import geopandas as gpd
from shapely.geometry import Point
from shapely.ops import unary_union
import pandas as pd
import shapely.wkt
from pathlib import Path

def validate_geo(data):
    """
    La función validate_geo valida la ubicación geográfica de las propiedades.
    Toma como parámetro un DataFrame de pandas.
    Asume que las columnas 'lat' y 'lon' existen en el DataFrame.
    Devuelve el DataFrame con los casos flageados.
    """
    # Initialize flag column if it doesn't exist
    if 'flag' not in data.columns:
        data['flag'] = None
    
    # Try to find the barrios file relative to this script
    current_dir = Path(__file__).parent
    barrios_path = current_dir.parent / 'barrios copy.csv'
    
    if not barrios_path.exists():
        # Fallback to absolute path if relative doesn't work
        barrios_path = '/Users/gerardoaboulafia/Projects/Property_price_prediction/Pipeline/barrios copy.csv'
    
    barrios = gpd.read_file(str(barrios_path))
    barrios['geometry'] = barrios['WKT'].apply(lambda x: shapely.wkt.loads(x))
    combined_polygon = unary_union(barrios['geometry'])

    # Máscaras de coordenadas presentes / faltantes
    mask_coords_ok = data[['lat', 'lon']].notna().all(axis=1)
    mask_coords_missing = data[['lat', 'lon']].isna().any(axis=1)

    # Inicializar en_capital como NaN y luego completar
    data['en_capital'] = pd.NA
    
    # Flag missing coordinates
    if mask_coords_missing.any():
        missing_flag = 'Missing coordinates'
        data.loc[mask_coords_missing, 'flag'] = (
            data.loc[mask_coords_missing, 'flag'].fillna('').apply(lambda x: x + '; ' if x else '') + missing_flag
        )

    # Evaluar puntos sólo donde hay coords
    if mask_coords_ok.any():
        puntos = data.loc[mask_coords_ok, ['lon', 'lat']].apply(
            lambda r: Point(r['lon'], r['lat']), axis=1
        )
        inside = puntos.apply(lambda p: combined_polygon.contains(p) or combined_polygon.touches(p))
        # Si tocás el borde, lo consideramos dentro (contains excluye el borde)
        data.loc[mask_coords_ok, 'en_capital'] = inside

        # Flagear fuera de CABA
        mask_outside = mask_coords_ok & (~inside)
        data.loc[mask_outside, 'flag'] = (
            data.loc[mask_outside, 'flag'].fillna('').apply(lambda x: x + '; ' if x else '') + 'Not in Capital Federal (polygon)'
        )

    # Limpiar separadores y normalizar flags vacíos a None
    data['flag'] = data['flag'].str.rstrip('; ').str.lstrip('; ').replace({'': None})

    return data
