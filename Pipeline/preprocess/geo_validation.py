import geopandas as gpd
from shapely.geometry import Point
from shapely.ops import unary_union
import pandas as pd
import shapely.wkt

def validate_geo(data):
    barrios = gpd.read_file('/Users/gerardoaboulafia/Library/Mobile Documents/com~apple~CloudDocs/UCA/Documentos/Cuatrimestre 4/Estadística Avanzada/TP/Pipeline/barrios copy.csv')
    barrios['geometry'] = barrios['WKT'].apply(lambda x: shapely.wkt.loads(x))
    combined_polygon = unary_union(barrios['geometry'])

    data_con_coords = data.dropna(subset=['latitud', 'longitud'])
    puntos = data_con_coords.apply(lambda row: Point(row['longitud'], row['latitud']), axis=1)
    data_con_coords.loc[:, 'en_capital'] = puntos.apply(lambda point: combined_polygon.contains(point))

    data = pd.concat([data_con_coords, data[data[['latitud', 'longitud']].isna().any(axis=1)]], ignore_index=True)
    data = data[data['en_capital'] == True]

    deleted = data[data['en_capital'] == False]

    print(f"Fueron eliminados {len(deleted)} registros que no estaban en CABA.")
    data = data.drop(columns=['en_capital'])
    
    return data
