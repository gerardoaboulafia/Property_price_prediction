import pandas as pd
import warnings

from preprocess.filter_data import filter_by_currency_place
from preprocess.regex_extraction import extract_features_regex
from preprocess.geo_validation import validate_geo
from preprocess.subte_distance import calculate_subte_distance
from preprocess.clean_outliers import clean_data_outliers

warnings.simplefilter(action='ignore', category=Warning)

# Función principal del pipeline de preprocesamiento
def preprocess_pipeline():
    # Pedir la ubicación del archivo por consola
    input_file = input("Introduce la ubicación del archivo de datos: ")

    # Cargar el dataset
    data = pd.read_csv(input_file)

    # Mantener solo las columnas relevantes iniciales
    data = data[['lat', 'lon', 'l1', 'l2', 'l3', 'rooms', 'surface_total',
                 'currency', 'title', 'description', 'property_type',
                 'operation_type', 'price']]

    print("\n--- Iniciando preprocesamiento ---")

    # 1. Filtrado por moneda y ubicación
    data = filter_by_currency_place(data)
    print("Filtrado por currency y lugar...")

    # 2. Extracción de features con expresiones regulares
    data = extract_features_regex(data)
    print("Extrayendo features con regex...")

    # 3. Validación geográfica
    data = validate_geo(data)
    print("Validando ubicación geográfica...")

    # 4. Cálculo de distancia al subte más cercano
    data = calculate_subte_distance(data)
    print("Calculando distancia a subte...")

    # Mantener solo las columnas finales relevantes
    data = data[['rooms_final', 'm2_final', 'distancia_subte_cercano',
                 'l3', 'property_type', 'price']]

    # 5. Limpieza de outliers
    data = clean_data_outliers(data)
    print("Limpieza de outliers...")

    # Guardar el dataset limpio
    output_file = "data/processed/datos_limpios.csv"
    data.to_csv(output_file, index=False)

    print(f"\nPreprocesamiento completado. Datos guardados en {output_file}")

if __name__ == "__main__":
    preprocess_pipeline()
