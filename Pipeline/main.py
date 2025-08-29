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

    # 1. Subetapa de filtrado por currency y l2
    data = filter_by_currency_place(data)

    print("\n")

    print("Filtrando data...")

    # 2. Subetapa de extracción de valores con RegEx
    data = extract_features_regex(data)

    print("Extrayendo features con expresiones regulares...")

    # 3. Subetapa de validación geográfica
    data = validate_geo(data)

    print("Validando que los departamentos se encuentren en CABA...")

    # 4. Subetapa de cálculo de distancia al subte más cercano
    print("Calculando la distancia al subte más cercano...")
    data = calculate_subte_distance(data)


    # 5. Subetapa de limpieza de outliers
    print("Limpiando outliers...")
    data = clean_data_outliers(data)


    

    print("Creando variables dummies...")

    # Definir col_dummies
    col_dummies = ['place_l3_Agronomía', 'place_l3_Almagro', 'place_l3_Balvanera', 'place_l3_Barracas', 'place_l3_Barrio Norte', 'place_l3_Belgrano', 'place_l3_Boca', 'place_l3_Boedo', 'place_l3_Caballito', 'place_l3_Catalinas', 'place_l3_Centro / Microcentro', 'place_l3_Chacarita', 'place_l3_Coghlan', 'place_l3_Colegiales', 'place_l3_Congreso', 'place_l3_Constitución', 'place_l3_Flores', 'place_l3_Floresta', 'place_l3_Las Cañitas', 'place_l3_Liniers', 'place_l3_Mataderos', 'place_l3_Monserrat', 'place_l3_Monte Castro', 'place_l3_Nuñez', 'place_l3_Once', 'place_l3_Palermo', 'place_l3_Parque Avellaneda', 'place_l3_Parque Centenario', 'place_l3_Parque Chacabuco', 'place_l3_Parque Chas', 'place_l3_Parque Patricios', 'place_l3_Paternal', 'place_l3_Pompeya', 'place_l3_Puerto Madero', 'place_l3_Recoleta', 'place_l3_Retiro', 'place_l3_Saavedra', 'place_l3_San Cristobal', 'place_l3_San Nicolás', 'place_l3_San Telmo', 'place_l3_Tribunales', 'place_l3_Velez Sarsfield', 'place_l3_Versalles', 'place_l3_Villa Crespo', 'place_l3_Villa Devoto', 'place_l3_Villa General Mitre', 'place_l3_Villa Lugano', 'place_l3_Villa Luro', 'place_l3_Villa Ortuzar', 'place_l3_Villa Pueyrredón', 'place_l3_Villa Real', 'place_l3_Villa Riachuelo', 'place_l3_Villa Santa Rita', 'place_l3_Villa Soldati', 'place_l3_Villa Urquiza', 'place_l3_Villa del Parque', 'type_Departamento', 'type_PH']

    # Añadir las columnas que faltan en data (rellenarlas con ceros)
    for col in col_dummies:
        if col not in data.columns:
            data[col] = 0

    # Eliminar las columnas adicionales que no están en col_dummies ni en las features numéricas
    numeric_features = ['rooms_final', 'm2_final', 'distancia_subte_cercano','price']
    required_columns = numeric_features + col_dummies
    data = data[[col for col in required_columns if col in data.columns]]

    # Escalar los datos
    scaler = StandardScaler()
    data[['rooms_final', 'm2_final', 'distancia_subte_cercano']] = scaler.fit_transform(
        data[['rooms_final', 'm2_final', 'distancia_subte_cercano']]
    )

    # Separar las features (X) y la etiqueta (y)
    X_train = data.drop('price', axis=1)
    #y_train = data['price']

    # Cargar el modelo preentrenado de XGBoost
    with open('models/model_xgboost.pkl', 'rb') as model_file:
        model = pickle.load(model_file)

    # Realizar predicciones
    print("Realizando predicciones...")
    print("\n")

    data['precio_prediccion'] = model.predict(X_train)

    # Calcular el error absoluto
    data['error_abs'] = abs(data['price'] - data['precio_prediccion'])

    # Calcular el error absoluto relativo
    data['error_rel'] = data['error_abs'] / data['price']

    # Guardar el resultado final en un nuevo archivo CSV
    output_file = 'predicciones.csv'
    data.to_csv(output_file, index=False)
    print(f"Pipeline completada. Resultados guardados en {output_file}")

    # Mostrar el error promedio
    print(f"Error absoluto promedio: {data['error_abs'].abs().mean()}")
    print(f"Error cuadrático medio: {((data['error_abs'] ** 2).mean()) ** 0.5}")
    print(f"Error absoluto relativo promedio: {data['error_rel'].abs().mean()}")

    # Mostrar el coeficiente de determinación R^2
    print(f"Coeficiente de determinación R^2: {r2_score(data['price'], data['precio_prediccion'])}")

    # Mostrar los cuartiles del error relativo
    print("\n")
    print("Cuartiles del error relativo:")
    print(data['error_rel'].describe())

    # Generar un histograma de la columna error_rel
    plt.figure(figsize=(10, 6))
    plt.hist(data['error_rel'], bins=30, edgecolor='black', alpha=0.7)
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
    start_pygame_interface()
