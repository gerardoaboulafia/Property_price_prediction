# Inventario de Datos

## 1. Dataset de Barrios de la Ciudad de Buenos Aires
- **Archivo:** `barrios.csv`
- **Origen:** Gobierno de la Ciudad de Buenos Aires
- **Contenido:** Polígonos en formato WKT que delimitan cada barrio de CABA.
- **Uso en pipeline:**
  - Validación geográfica → verificar si una propiedad realmente se encuentra dentro de CABA.
  - Construcción de un `MultiPolygon` para flaggear propiedades fuera de Capital.

---

## 2. Estaciones de Subte
- **Archivo:** `estaciones-de-subte.csv`
- **Origen:** Gobierno de la Ciudad de Buenos Aires
- **Contenido:** Coordenadas (`lat`, `long`) de todas las estaciones de subte.
- **Uso en pipeline:**
  - Cálculo de la distancia de cada propiedad a la estación más cercana.
  - Generación de la feature `distancia_subte_cercano`, usada como feature en los modelos.

---

## 3. Dataset de Validación (Properati para alumnos)
- **Archivo:** `properaty_dataset_alumnos.csv`
- **Origen:** CSV provisto en Estadística Avanzada
- **Contenido:** Subconjunto preparado con propiedades en CABA. Cuenta con 200.000 filas.
- **Uso en pipeline:**
  - Se usa para entrenar el modelo.
  - Se aplican:
    - Filtros por moneda, ubicación y tipo de propiedad.
    - Extracción de features con RegEx.
    - Validación geográfica (CABA).
    - Cálculo de distancia a subte.
    - Limpieza de outliers.

---

## 4. Dataset de Serving (Properati Argentina)
- **Archivo:** `entrenamiento.csv` (Kaggle – `alejandroczernikier/properati-argentina-dataset`)
- **Contenido:** Propiedades con atributos como lat/lon, precio, tipo, ambientes, superficie, etc. Cuenta con 1 millón de filas aproximadamente
- **Uso en pipeline:**
  - Conjunto principal para simular datos de producción.
  - Permite medir error en datos que no fueron usados en el ajuste de hiperparámetros.
