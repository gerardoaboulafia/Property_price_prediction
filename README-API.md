## **1\. Descripción general de la API**

La API permite predecir el precio de propiedades en Buenos Aires, utilizando un modelo de XGBoost entrenado. La API recibe datos de propiedades como ubicación, superficie, cantidad de habitaciones, etc., y devuelve una predicción del precio de la propiedad.  
El pipeline de la API realiza varias validaciones y transformaciones antes de pasar los datos al modelo de predicción, asegurando que solo se predigan precios para propiedades válidas y correctamente formateadas.

## **2\. Setup**

Requisitos: asegurarse de tener las dependencias necesarias instaladas:

Además la API espera que los siguientes archivos estén presentes:

* Pipeline/models/xgb\_pipeline3.pkl, el modelo XGBoost entrenado.  
  * Pipeline/estaciones-de-subte copy.csv, datos de estaciones de subte.  
  * Pipeline/barrios copy.csv, datos geográficos de los barrios de Buenos Aires.

## **3\. Ejecutar la API**

Para correr la API en tu máquina local, se utiliza el siguiente comando:

`uvicorn app.main:app --reload --host 0.0.0.0 --port 8000`

Esto lanzará el servidor de la API en `http://localhost:8000`.

* API: [http://localhost:8000](http://localhost:8000)  
* Documentación interactiva (Swagger): [http://localhost:8000/docs](http://localhost:8000/docs)  
* Documentación alternativa (ReDoc): [http://localhost:8000/redoc](http://localhost:8000/redoc)

## **4\. EndPoints de la API**

En una API, los endpoints son URLs específicas a las que los usuarios o sistemas pueden hacer solicitudes para acceder a diferentes funcionalidades de la aplicación.  
Cada endpoint está asociado con una acción específica que realiza el servidor. Los endpoints están estructurados en función de las necesidades de la API, y la acción que se toma depende del método HTTP utilizado (como GET, POST, PUT, DELETE).

La API dispone de los siguientes endpoints:

Health Check

* **GET `/`:** Devuelve el estado de la API y la información del pipeline, útil para saber si la API está en funcionamiento.

Este endpoint se usa para verificar si la API está funcionando correctamente. Al enviar una solicitud GET a este endpoint, obtendrás un mensaje de estado que indica si la API está activa o si tiene algún problema.

Información del Modelo

* **GET `/model/info`:** Devuelve información sobre el modelo cargado, como el tipo de modelo, parámetros y estado actual.

Este endpoint proporciona información sobre el modelo cargado en la API, como el tipo de modelo (por ejemplo, XGBoost), sus parámetros, etc. Es útil para conocer el estado del modelo y cómo está configurado.

Predicción del Precio

* **POST `/predict`:** Predice el precio de una propiedad en base a los datos enviados. Recibe un JSON con los datos de la propiedad y devuelve el precio estimado.

Este es el endpoint principal de la API. Aquí es donde se realiza la predicción del precio de la propiedad. Recibe un JSON con las características de la propiedad (por ejemplo, ubicación, cantidad de habitaciones, precio, etc.) y devuelve el precio estimado.

## **5\. Input y Output Schema**

**Input Schema**

La solicitud **POST `/predict`** debe enviar un JSON con la siguiente estructura de datos:

**`{`**  
  **`"id": 1,`**  
  **`"ad_type": "property",`**  
  **`"start_date": "2023-01-01",`**  
  **`"end_date": "2023-12-31",`**  
  **`"created_on": "2023-01-01",`**  
  **`"lat": -34.6037,`**  
  **`"lon": -58.3816,`**  
  **`"l1": "Argentina",`**  
  **`"l2": "Capital Federal",`**  
  **`"l3": "Palermo",`**  
  **`"l4": null,`**  
  **`"l5": null,`**  
  **`"l6": null,`**  
  **`"rooms": 2.0,`**  
  **`"bedrooms": 1.0,`**  
  **`"bathrooms": 1.0,`**  
  **`"surface_total": 65.0,`**  
  **`"surface_covered": 60.0,`**  
  **`"currency": "USD",`**  
  **`"price_period": "monthly",`**  
  **`"title": "Departamento 2 ambientes 65m2 Palermo",`**  
  **`"description": "Hermoso departamento de 2 ambientes en Palermo, 65 metros cuadrados",`**  
  **`"property_type": "Departamento",`**  
  **`"operation_type": "Venta",`**  
  **`"price": 185000.0`**  
**`}`**

Los campos son los siguientes:

* **`id`:** Identificador único de la propiedad.

* **`ad_type`:** Tipo de anuncio (si es propiedad).

* **`start_date` y `end_date`:** Periodo de vigencia del anuncio.

* **`lat` y `lon`:** Coordenadas de la propiedad.

* **`l1`, `l2`, `l3`:** Jerarquía de ubicación (país, provincia, barrio).

* **`rooms`, `bedrooms`, `bathrooms`:** Características del inmueble.

* **`surface_total` y `surface_covered`:** Metros cuadrados.

* **`currency`:** Moneda de la propiedad (debe ser USD).

* **`price`:** Precio inicial de la propiedad.

**Output Schema**

La respuesta de la predicción tiene la siguiente estructura:

**`{`**  
  **`"predicted_price": 189500.50,`**  
  **`"preprocessing_flags": null,`**  
  **`"is_valid_for_prediction": true,`**  
  **`"input_features": {`**  
    **`"place_l3": "Palermo",`**  
    **`"type": "Departamento",`**  
    **`"rooms_final": 2.0,`**  
    **`"m2_final": 65.0,`**  
    **`"distancia_subte_cercano": 0.85`**  
  **`}`**  
**`}`**

Los campos son los siguientes:

* **`predicted_price`:** Precio estimado de la propiedad en USD.

* **`preprocessing_flags`:** Indica si hubo errores durante el preprocesamiento (por ejemplo, datos invalidos).

* **`is_valid_for_prediction`:** Booleano que indica si los datos pasaron la validación.

* **`input_features`:** Características finales utilizadas para hacer la predicción, luego del preprocesamiento (ej. barrio, tipo de propiedad, metros cuadrados, distancia al subte).

## **6\. Pipeline de Preprocesamiento**

El pipeline de preprocesamiento realiza los siguientes pasos:

1. Filtrado por Moneda y Ubicación: Valida que la moneda sea USD y que la ubicación esté dentro de Capital Federal, Buenos Aires.  
2. Extracción de Características con RegEx: Se extraen datos del título y la descripción, como el número de habitaciones, superficie cubierta y total, y otros atributos relevantes.  
3. Validación Geográfica: Verifica que las coordenadas (lat, lon) estén dentro de los límites de la Ciudad de Buenos Aires.  
4. Cálculo de Distancia al Subte: Se calcula la distancia de la propiedad a la estación de subte más cercana utilizando los datos de las estaciones.  
5. Limpieza de Outliers: Se detectan y limpian los outliers en precio, superficie, y número de habitaciones, utilizando métodos estadísticos.

## **7\. Pruebas**

Puedes usar el script de prueba para validar el funcionamiento de la API a través del Powershell: `python test_api.py`

Este script prueba:

* El estado de la API.  
* La predicción válida para una propiedad.  
* Manejo de propiedades inválidas (por ejemplo, propiedades con moneda incorrecta o fuera del área de Buenos Aires).

## **8\. Uso con curl**

Aquí te mostramos cómo interactuar con la API usando `curl`.

**Chequeo de Salud**  
`curl -X GET "http://localhost:8000/"`

**Predicción de Precio**  
`curl -X POST "http://localhost:8000/predict" \`  
  `-H "Content-Type: application/json" \`  
  `-d '{`  
    `"id": 1,`  
    `"ad_type": "property",`  
    `"start_date": "2023-01-01",`  
    `"end_date": "2023-12-31",`  
    `"created_on": "2023-01-01",`  
    `"lat": -34.6037,`  
    `"lon": -58.3816,`  
    `"l1": "Argentina",`  
    `"l2": "Capital Federal",`  
    `"l3": "Palermo",`  
    `"rooms": 2.0,`  
    `"bedrooms": 1.0,`  
    `"bathrooms": 1.0,`  
    `"surface_total": 65.0,`  
    `"surface_covered": 60.0,`  
    `"currency": "USD",`  
    `"price_period": "monthly",`  
    `"title": "Departamento 2 ambientes 65m2 Palermo",`  
    `"description": "Hermoso departamento de 2 ambientes en Palermo",`  
    `"property_type": "Departamento",`  
    `"operation_type": "Venta",`  
    `"price": 185000.0`  
  `}'`

Esto te devolverá el precio estimado de la propiedad.

