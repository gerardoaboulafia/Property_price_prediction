import pygame
import pandas as pd
import pickle
from preprocess.filter_data import filter_by_currency_place
from preprocess.regex_extraction import extract_features_regex
from preprocess.geo_validation import validate_geo
from preprocess.subte_distance import calculate_subte_distance
from preprocess.clean_outliers import clean_data_outliers
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import r2_score
import warnings
import matplotlib.pyplot as plt
warnings.simplefilter(action='ignore', category=Warning)

# Función principal para el pipeline de predicción
def main_pipeline():
    # Pedir la ubicación del archivo por consola
    input_file = input("Introduce la ubicación del archivo de datos: ")

    # Cargar el dataset
    data = pd.read_csv(input_file)

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

    # keep only 'lat,'lon', 'l1', 'l2', 'l3','rooms','surface_total', 'currency', 'title', 'description', 'property_type', 'operation_type','price'
    data = data[['lat', 'lon', 'l1', 'l2', 'l3', 'rooms', 'surface_total', 'currency', 'title', 'property_type', 'operation_type', 'price']]

    # 1. Subetapa de filtrado por currency y l2
    print("\n")
    print("Filtrando data...")

    data = filter_by_currency_place(data)

    print(data.head())

    # 2. Subetapa de extracción de valores con RegEx
    print("Extrayendo features con expresiones regulares...")

    data = extract_features_regex(data)

    print(data.head())

    # 3. Subetapa de validación geográfica
    print("Validando que los departamentos se encuentren en CABA...")

    data = validate_geo(data)

    print(data.head())

    
    # 4. Subetapa de cálculo de distancia al subte más cercano
    print("Calculando la distancia al subte más cercano...")
    data = calculate_subte_distance(
    data,
    r"C:\Users\mical\OneDrive - UCA\UCA\2025\2do cuatrimestre\Laboratorio II\Property_price_prediction\Pipeline\estaciones-de-subte copy.csv"
)
    
    print(data.head())

    # keep only relevant columns: place_l3	type	rooms_final	m2_final	distancia_subte_cercano    price
    data = data[['rooms_final', 'm2_final', 'distancia_subte_cercano', 'l3', 'property_type', 'price', 'flag']]

    # 5. Subetapa de limpieza de outliers
    print("Limpiando outliers...")
    data = clean_data_outliers(data)

    print(data.head())

    # Guardar el dataset limpio
    output_file = "data/processed/datos_limpios_1.csv"
    data.to_csv(output_file, index=False)

    # Separamos los datos con los que se trabajará (aquellas filas en donde 'flag' es None) 
    valid_data = data[data['flag'].isnull()]
    invalid_data = data[data['flag'].notnull()]
    print(f"Datos válidos para predicción: {valid_data.shape[0]} filas")
    print(f"Datos inválidos para predicción: {invalid_data.shape[0]} filas")

    # Seleccionar el subconjunto de columnas numéricas para escalar
    numeric_features = ['rooms_final', 'm2_final', 'distancia_subte_cercano']

    # Escalar los datos con el scaler que se ajustó a los datos de entrenamiento
    with open ('models/scaler.pkl', 'rb') as scaler_file:
        scaler = pickle.load(scaler_file)
    valid_data[numeric_features] = scaler.transform(valid_data[numeric_features])

    # Separar las features (X) y la etiqueta (y)
    X_train = valid_data.drop('price', axis=1)
    #y_train = valid_data['price']

    # Cargar el modelo preentrenado de XGBoost
    with open('models/model_xgboost.pkl', 'rb') as model_file:
        model = pickle.load(model_file)

    # Realizar predicciones
    print("Realizando predicciones...")
    print("\n")

    valid_data['precio_prediccion'] = model.predict(X_train)

    # Calculamos el r cuadrado para la predicción
    r2 = r2_score(valid_data['price'], valid_data['precio_prediccion'])
    print(f"Coeficiente de determinación R^2: {r2}")

    # Calcular el error absoluto
    valid_data['error_abs'] = abs(valid_data['price'] - valid_data['precio_prediccion'])

    # Calcular el error absoluto relativo
    valid_data['error_rel'] = valid_data['error_abs'] / valid_data['price']

    # Guardar el resultado final en un nuevo archivo CSV
    output_file = 'predicciones.csv'

    # Concatenar valid_data con invalid_data
    final_data = pd.concat([valid_data, invalid_data], axis=0)

    final_data.to_csv(output_file, index=False)
    print(f"Pipeline completada. Resultados guardados en {output_file}")

    # Mostrar el error promedio
    print(f"Error absoluto promedio: {valid_data['error_abs'].abs().mean()}")
    print(f"Error cuadrático medio: {((valid_data['error_abs'] ** 2).mean()) ** 0.5}")
    print(f"Error absoluto relativo promedio: {valid_data['error_rel'].abs().mean()}")

    # Mostrar el coeficiente de determinación R^2
    print(f"Coeficiente de determinación R^2: {r2_score(valid_data['price'], valid_data['precio_prediccion'])}")

    # Mostrar los cuartiles del error relativo
    print("\n")
    print("Cuartiles del error relativo:")
    print(valid_data['error_rel'].describe())

    # Generar un histograma de la columna error_rel
    plt.figure(figsize=(10, 6))
    plt.hist(valid_data['error_rel'], bins=30, edgecolor='black', alpha=0.7)
    plt.title('Distribución del Error Relativo')
    plt.xlabel('Error Relativo')
    plt.ylabel('Frecuencia')
    plt.grid(True)

    # Guardar el histograma como imagen
    histograma = 'error_rel_histogram.png'
    plt.savefig(histograma)
    plt.close()  # Cierra el gráfico para liberar memoria

    print(f"Histograma guardado como {histograma}")

    # Filtrar datos con error relativo menor que 1
    filtered_data = data[data['error_rel'] < 1]

    # Generar un histograma de la columna error_rel
    plt.figure(figsize=(10, 6))
    plt.hist(filtered_data['error_rel'], bins=30, edgecolor='black', alpha=0.7)
    plt.title('Distribución del Error Relativo (< 1)')
    plt.xlabel('Error Relativo')
    plt.ylabel('Frecuencia')
    plt.grid(True)

    # Guardar el histograma como imagen
    histograma_f = 'filtered_error_rel_histogram.png'
    plt.savefig(histograma_f)
    plt.close()

    print(f"Histograma filtrado guardado como {histograma_f}")



# Función para inicializar Pygame y crear el banner con el botón
def start_pygame_interface():
    pygame.init()

    # Definir colores
    WHITE = (255, 255, 255)
    BLUE = (0, 128, 255)

    # Cargar la imagen del banner y obtener sus proporciones
    banner_image = pygame.image.load('banner.png')  # Usar el banner proporcionado
    banner_width, banner_height = banner_image.get_size()

    # Escalar la imagen del banner manteniendo las proporciones
    window_width = 800  # Fijar el ancho de la ventana
    scale_factor = window_width / banner_width
    scaled_banner = pygame.transform.scale(banner_image, (window_width, int(banner_height * scale_factor)))

    # Configurar pantalla
    window_height = int(banner_height * scale_factor) + 200  # Altura de la ventana con espacio para el botón
    screen = pygame.display.set_mode((window_width, window_height))
    pygame.display.set_caption("Predicción de Precios de Propiedades")

    # Definir el botón y ajustar la posición debajo del banner
    button_rect = pygame.Rect(300, int(banner_height * scale_factor) + 50, 200, 60)  # Subir el botón justo debajo del banner

    # Bucle principal de Pygame
    running = True
    while running:
        screen.fill(WHITE)

        # Detectar eventos
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.MOUSEBUTTONDOWN:
                if button_rect.collidepoint(event.pos):
                    # Ejecutar el pipeline cuando se presiona el botón
                    main_pipeline()

        # Dibujar el banner ajustado
        screen.blit(scaled_banner, (0, 0))  # Colocar el banner en la parte superior

        # Dibujar el botón
        pygame.draw.rect(screen, BLUE, button_rect)
        font = pygame.font.SysFont(None, 40)
        text = font.render("Predecir", True, WHITE)
        screen.blit(text, (button_rect.x + 45, button_rect.y + 15))

        # Actualizar la pantalla
        pygame.display.flip()

    pygame.quit()

if __name__ == "__main__":
    main_pipeline()
