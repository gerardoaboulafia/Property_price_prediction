# from preprocess.db_utils import get_connection, download_from_mysql, upload_dataframe_to_mysql
# from preprocess.filter_data import filter_by_currency_place
# from preprocess.regex_extraction import extract_features_regex
# from preprocess.geo_validation import validate_geo
# from preprocess.subte_distance import calculate_subte_distance
# from preprocess.clean_outliers import clean_data_outliers
from Pipeline.preprocess.db_utils import get_connection, download_from_mysql, upload_dataframe_to_mysql
from Pipeline.preprocess.filter_data import filter_by_currency_place
from Pipeline.preprocess.regex_extraction import extract_features_regex
from Pipeline.preprocess.geo_validation import validate_geo
from Pipeline.preprocess.subte_distance import calculate_subte_distance
from Pipeline.preprocess.clean_outliers import clean_data_outliers
import pandas as pd
import warnings

warnings.simplefilter(action='ignore', category=Warning)


def preprocess_pipeline():
    # 1. Conexión a MySQL
    conn = get_connection(user="labo_ame_agus", password="ameagusmica", host="172.29.208.1", port=3307, database="laboratorioII")

    # 2. Descargar dataset original desde MySQL
    data = download_from_mysql("raw_data", conn)

    # Renombrar columnas del dataset a las que espera el pipeline
    data = data.rename(columns={
        "latitud": "lat",
        "longitud": "lon",
        "place_l2": "l1",
        "place_l3": "l2",
        "place_l4": "l3",
        "property_rooms": "rooms",
        "property_surface_total": "surface_total",
        "property_currency": "currency",
        "property_title": "title",
        "operation": "operation_type",
        "property_price": "price"
    })

    # Mantener solo las columnas relevantes iniciales
    data = data[['lat', 'lon', 'l1', 'l2', 'l3', 'rooms', 'surface_total',
                 'currency', 'title', 'property_type',
                 'operation_type', 'price']]

    print("\n--- Iniciando preprocesamiento ---")

    # 1. Filtrado por moneda y ubicación

    print("\n")
    print("Filtrando los datos necesarios...")
    print("\n")

    data = filter_by_currency_place(data)

    # 2. Extracción de features con expresiones regulares
    print("\n")
    print("Extrayendo features con expresiones regulares...")
    print("\n")

    data = extract_features_regex(data)

    # 3. Validación geográfica
    print("\n")
    print("Validando que los departamentos se encuentren en CABA...")
    print("\n")

    data = validate_geo(data)


    # 4. Cálculo de distancia al subte más cercano
    print("\n")
    print("Calculando la distancia al subte más cercano...")
    print("\n")

    data['lat'] = pd.to_numeric(data['lat'], errors='coerce')
    data['lon'] = pd.to_numeric(data['lon'], errors='coerce')


    data = calculate_subte_distance(
    data,
    r"C:\Users\mical\OneDrive - UCA\UCA\2025\2do cuatrimestre\Laboratorio II\Property_price_prediction\Pipeline\estaciones-de-subte copy.csv"
)

    # Mantener solo las columnas finales relevantes
    data = data[['rooms_final', 'm2_final', 'distancia_subte_cercano',
                 'l2', 'property_type', 'price', 'flag']]

    # 5. Limpieza de outliers

    # Asegurar columnas numéricas
    for col in ['price', 'rooms_final', 'm2_final']:
        data[col] = pd.to_numeric(data[col], errors='coerce')


    print("\n")
    print("Limpiando outliers...")
    print("\n")
    data = clean_data_outliers(data)

    # 5. Subir a MySQL directamente
    upload_dataframe_to_mysql(data, "processed_data", conn)

    # 6. Cerrar conexión
    conn.close()
    print("Preprocesamiento completado y datos subidos a MySQL (tabla processed_data)")

if __name__ == "__main__":
    preprocess_pipeline()

def preprocess_data(data):
    df = pd.DataFrame(data)
    df = df.fillna(df.mean(numeric_only=True))
    return df

