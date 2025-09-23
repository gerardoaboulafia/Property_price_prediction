from anyio import Path
import geopandas as gpd
from shapely.geometry import Point
from shapely.ops import unary_union
import pandas as pd
import shapely.wkt


def validate_geo(data):
    """
    La función validate_geo valida la ubicación geográfica de las propiedades.
    Toma como parámetro un DataFrame de pandas.
    Asume que las columnas 'lat' y 'lon' existen en el DataFrame.
    Devuelve el DataFrame con los casos flageados.
    """

    barrios_path = Path("C:/Users/mical/OneDrive - UCA/UCA/2025/2do cuatrimestre/Laboratorio II/Property_price_prediction/Pipeline/barrios copy.csv")
    #barrios = gpd.read_file('Pipeline/barrios copy.csv')
    # Leer CSV de barrios
    barrios = pd.read_csv(barrios_path, encoding="latin1")

    # Convertir columna WKT en geometrías
    barrios['geometry'] = barrios['WKT'].apply(shapely.wkt.loads)

    # Pasar a GeoDataFrame
    barrios = gpd.GeoDataFrame(barrios, geometry='geometry', crs="EPSG:4326")

    # Crear polígono combinado
    combined_polygon = unary_union(barrios['geometry'])

    barrios['geometry'] = barrios['WKT'].apply(lambda x: shapely.wkt.loads(x))
    combined_polygon = unary_union(barrios['geometry'])

    # Máscaras de coordenadas presentes / faltantes
    mask_coords_ok = data[['lat', 'lon']].notna().all(axis=1)

    # Inicializar en_capital como NaN y luego completar
    data['en_capital'] = pd.NA

    # Evaluar puntos sólo donde hay coords
    if mask_coords_ok.any():
        puntos = data.loc[mask_coords_ok, ['lat', 'lon']].apply(
            lambda r: Point(r['lon'], r['lat']), axis=1
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

    p = Point(-58.429204, -34.598973)  # lon, lat
    print(combined_polygon.contains(p))

    return data