import geopandas as gpd
from shapely.geometry import Point
from shapely.ops import unary_union
import pandas as pd
import shapely.wkt

def validate_geo(data):
    barrios = gpd.read_file('Pipeline/barrios copy.csv')
    #barrios = gpd.read_file('/Users/gerardoaboulafia/Library/Mobile Documents/com~apple~CloudDocs/UCA/Documentos/Cuatrimestre 4/Estadística Avanzada/TP/Pipeline/barrios copy.csv')
    barrios['geometry'] = barrios['WKT'].apply(lambda x: shapely.wkt.loads(x))
    combined_polygon = unary_union(barrios['geometry'])

    # Máscaras de coordenadas presentes / faltantes
    mask_coords_ok = data[['latitud', 'longitud']].notna().all(axis=1)
    mask_coords_missing = ~mask_coords_ok

    # Inicializar en_capital como NaN y luego completar
    data['en_capital'] = pd.NA

    # Evaluar puntos sólo donde hay coords
    if mask_coords_ok.any():
        puntos = data.loc[mask_coords_ok, ['longitud', 'latitud']].apply(
            lambda r: Point(r['longitud'], r['latitud']), axis=1
        )
        inside = puntos.apply(lambda p: combined_polygon.contains(p) or combined_polygon.touches(p))
        # Si tocás el borde, lo consideramos dentro (contains excluye el borde)
        data.loc[mask_coords_ok, 'en_capital'] = inside

        # Flagear fuera de CABA
        mask_outside = mask_coords_ok & (~inside)
        data.loc[mask_outside, 'flag'] = (
            data.loc[mask_outside, 'flag'].fillna('') + 'Not in Capital Federal (polygon); '
        )

    # Limpiar separadores y normalizar flags vacíos a None
    data['flag'] = data['flag'].str.rstrip('; ').replace({'': None})

    return data