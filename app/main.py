from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from typing import Optional, List
import pandas as pd
import numpy as np
import sys
import os
import joblib
from pathlib import Path

# Add the Pipeline directory to the Python path
pipeline_dir = Path(__file__).parent.parent / "Pipeline"
sys.path.append(str(pipeline_dir))

# Import preprocessing functions
from preprocess.filter_data import filter_by_currency_place
from preprocess.regex_extraction import extract_features_regex
from preprocess.geo_validation import validate_geo
from preprocess.subte_distance import calculate_subte_distance
from preprocess.clean_outliers import clean_data_outliers

app = FastAPI(
    title="Property Price Prediction API",
    description="API for predicting property prices using XGBoost model with preprocessing pipeline",
    version="1.0.0"
)

# Load the trained model
MODEL_PATH = pipeline_dir / "models" / "model_api_test.pkl"
SUBTE_STATIONS_PATH = pipeline_dir / "estaciones-de-subte copy.csv"
BARRIOS_CSV_PATH = pipeline_dir / "barrios copy.csv"

try:
    model = joblib.load(MODEL_PATH)
    print(f"Model loaded successfully from {MODEL_PATH}")
except Exception as e:
    print(f"Error loading model: {e}")
    model = None

# --- CLASE PRINCIPAL MODIFICADA CON ALIAS ---

class PropertyInput(BaseModel):
    """Input schema matching the original dataset structure"""
    # Usamos alias para forzar el nombre en español en la documentación (Swagger) y en la entrada JSON.
    id: int = Field(..., alias="Identificador", description="Identificador único para la propiedad")
    ad_type: str = Field(..., alias="Tipo_de_Anuncio", description="Tipo de anuncio")
    start_date: str = Field(..., alias="Fecha_de_Inicio", description="Fecha de inicio de la publicación")
    end_date: str = Field(..., alias="Fecha_de_Fin", description="Fecha de fin de la publicación")
    created_on: str = Field(..., alias="Fecha_de_Creacion", description="Fecha en que se creó la publicación")
    
    # Coordenadas
    lat: Optional[float] = Field(None, alias="Latitud", description="Coordenada de latitud")
    lon: Optional[float] = Field(None, alias="Longitud", description="Coordenada de longitud")
    
    # 📌 NIVELES DE UBICACIÓN SOLICITADOS (L1, L2, L3)
    l1: str = Field(..., alias="Ciudad", description="Nivel de ubicación 1 (L1 - Ciudad principal o Región)")
    l2: str = Field(..., alias="Barrio", description="Nivel de ubicación 2 (L2 - Barrio o Comuna)")
    l3: str = Field(..., alias="Sub_barrio", description="Nivel de ubicación 3 (L3 - Sub-barrio o área específica)")
    
    l4: Optional[str] = Field(None, alias="Nivel_de_Ubicacion_4", description="Nivel de ubicación 4")
    l5: Optional[str] = Field(None, alias="Nivel_de_Ubicacion_5", description="Nivel de ubicación 5")
    l6: Optional[float] = Field(None, alias="Nivel_de_Ubicacion_6", description="Nivel de ubicación 6")
    
    # Características
    rooms: Optional[float] = Field(None, alias="Ambientes", description="Cantidad de ambientes")
    bedrooms: Optional[float] = Field(None, alias="Dormitorios", description="Cantidad de dormitorios")
    bathrooms: Optional[float] = Field(None, alias="Banios", description="Cantidad de baños")
    surface_total: Optional[float] = Field(None, alias="Superficie_Total_m2", description="Área total en m²")
    surface_covered: Optional[float] = Field(None, alias="Superficie_Cubierta_m2", description="Área cubierta en m²")
    
    # Precio y tipo
    currency: str = Field(..., alias="Moneda", description="Moneda del precio (ej: USD)")
    price_period: str = Field(..., alias="Periodo_de_Precio", description="Período de precio (ej: mensual)")
    title: str = Field(..., alias="Titulo_del_Anuncio", description="Título de la publicación de la propiedad")
    description: str = Field(..., alias="Descripcion_del_Anuncio", description="Descripción de la propiedad")
    property_type: str = Field(..., alias="Tipo_de_Propiedad", description="Tipo de propiedad (ej: Departamento, Casa, PH)")
    operation_type: str = Field(..., alias="Tipo_de_Operacion", description="Tipo de operación (ej: Venta, Alquiler)")
    price: float = Field(..., alias="Precio", description="Precio de la propiedad")

    class Config:
        # Permite que la API use los nombres internos (l1) o los alias (Ciudad) para llenar el modelo.
        allow_population_by_field_name = True
        # Fuerza a Pydantic a usar los ALIAS para la generación del esquema OpenAPI (Swagger).
        by_alias = True
        
        schema_extra = {
            # EL EJEMPLO DEBE USAR LAS NUEVAS CLAVES EN ESPAÑOL (ALIAS)
            "example": {
                "Identificador": 1,
                "Tipo_de_Anuncio": "property",
                "Fecha_de_Inicio": "2023-01-01",
                "Fecha_de_Fin": "2023-12-31",
                "Fecha_de_Creacion": "2023-01-01",
                "Latitud": -34.5900, 
                "Longitud": -58.4200, 
                "Ciudad": "Argentina",
                "Barrio": "Capital Federal",
                "Sub_barrio": "Palermo",
                "Nivel_de_Ubicacion_4": None,
                "Nivel_de_Ubicacion_5": None,
                "Nivel_de_Ubicacion_6": None,
                "Ambientes": 2.0,
                "Dormitorios": 1.0,
                "Banios": 1.0,
                "Superficie_Total_m2": 65.0,
                "Superficie_Cubierta_m2": 60.0,
                "Moneda": "USD",
                "Periodo_de_Precio": "monthly",
                "Titulo_del_Anuncio": "Departamento 2 ambientes 65m2 Palermo",
                "Descripcion_del_Anuncio": "Hermoso departamento de 2 ambientes en Palermo, 65 metros cuadrados",
                "Tipo_de_Propiedad": "Departamento",
                "Tipo_de_Operacion": "Venta",
                "Precio": 185000.0
            }
        }

# --- CLASES DE SALIDA Y ESTADO (SIN CAMBIOS) ---

class PredictionOutput(BaseModel):
    """Output schema for predictions"""
    predicted_price: float = Field(..., description="Predicted price in USD")
    preprocessing_flags: Optional[str] = Field(None, description="Any flags from preprocessing")
    is_valid_for_prediction: bool = Field(..., description="Whether the data passed validation")
    input_features: dict = Field(..., description="Features used for prediction")

class PipelineStatus(BaseModel):
    """Health check response"""
    status: str
    model_loaded: bool
    pipeline_components: List[str]

# --- FUNCIONES DE PREPROCESAMIENTO Y PREDICCIÓN (SIN CAMBIOS EN LA LÓGICA) ---

def preprocess_data(property_data: PropertyInput) -> pd.DataFrame:
    """
    Process the input data through the same pipeline as the notebook
    (Usa los nombres de variables internos: property_data.l1, property_data.rooms, etc.)
    """
    # Convert to DataFrame with required columns for pipeline
    data = pd.DataFrame([{
        'lat': property_data.lat,
        'lon': property_data.lon,
        'l1': property_data.l1,
        'l2': property_data.l2,
        'l3': property_data.l3,
        'rooms': property_data.rooms,
        'surface_total': property_data.surface_total,
        'currency': property_data.currency,
        'title': property_data.title,
        'description': property_data.description,
        'property_type': property_data.property_type,
        'operation_type': property_data.operation_type,
        'price': property_data.price
    }])
    
    # 1. Filter by currency and place
    data = filter_by_currency_place(data)
    
    # 2. Extract features using RegEx
    data = extract_features_regex(data)
    
    # Verificar las coordenadas antes de validarlas
    print(f"Coordenada a verificar: lat = {data['lat'].iloc[0]}, lon = {data['lon'].iloc[0]}")

    # 3. Validate geography
    data = validate_geo(data, str(BARRIOS_CSV_PATH))
    
    # 4. Calculate distance to nearest subway station
    data = calculate_subte_distance(data, str(SUBTE_STATIONS_PATH))
    
    # 5. Keep only relevant columns (as in notebook)
    data = data[['rooms_final', 'm2_final', 'distancia_subte_cercano', 'l2', 'property_type', 'price', 'flag']]
    
    # 6. Clean outliers
    data = clean_data_outliers(data)
    
    return data

@app.post("/predict", response_model=PredictionOutput)
async def predict_price(property_data: PropertyInput):
    """
    Predict property price using the trained XGBoost model
    """
    if model is None:
        raise HTTPException(status_code=500, detail="Model not loaded")
    
    try:
        # Preprocess the data
        processed_data = preprocess_data(property_data)
        
        # Check if data is valid for prediction (no flags)
        is_valid = processed_data['flag'].isnull().iloc[0]
        flag_value = processed_data['flag'].iloc[0] if not is_valid else None
        
        if not is_valid:
            return PredictionOutput(
                predicted_price=0.0,
                preprocessing_flags=flag_value,
                is_valid_for_prediction=False,
                input_features={}
            )
        
        # Prepare features for prediction (following notebook transformations)
        valid_data = processed_data[processed_data['flag'].isnull()]
        X_features = valid_data.drop(columns=['price'])

        # Convertir tipos numéricos primero y limpiar
        for col in ["rooms_final", "m2_final", "distancia_subte_cercano"]:
            X_features[col] = pd.to_numeric(X_features[col], errors="coerce")

        # Reemplazar valores no finitos en columnas numéricas
        X_features[["rooms_final", "m2_final", "distancia_subte_cercano"]] = \
            X_features[["rooms_final", "m2_final", "distancia_subte_cercano"]].replace([np.inf, -np.inf], np.nan).fillna(0)

        # Asegurar que 'flag' exista y sea string
        if 'flag' not in X_features.columns:
            X_features['flag'] = "None"

        # Rellenar NaN en las categóricas antes de convertir
        for col in ["l2", "property_type", "flag"]:
            if col in X_features.columns:
                X_features[col] = X_features[col].fillna("None").astype("category")
        
        # Make prediction
        prediction = model.predict(X_features)[0]
        
        # Prepare feature dictionary for response
        feature_dict = X_features.iloc[0].to_dict()
        
        return PredictionOutput(
            predicted_price=float(prediction),
            preprocessing_flags=None,
            is_valid_for_prediction=True,
            input_features=feature_dict
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Prediction error: {str(e)}")

@app.get("/model/info")
async def model_info():
    """Get information about the loaded model"""
    if model is None:
        raise HTTPException(status_code=500, detail="Model not loaded")
    
    try:
        # Try to get model information
        info = {
            "model_type": type(model)._name_,
            "model_path": str(MODEL_PATH),
            "expected_features": ['rooms_final', 'm2_final', 'distancia_subte_cercano', 'l2', 'property_type', 'price', 'flag']
        }
        
        # If it's a pipeline, try to get more details
        if hasattr(model, 'steps'):
            info["pipeline_steps"] = [step[0] for step in model.steps]
            
        return info
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting model info: {str(e)}")

# --- MANEJO DE ERRORES Y DICCIONARIO ACTUALIZADO ---

# Si tienes un archivo 'app/health.py' debes asegurarte de que exista:
# from app.health import router as health_router
# app.include_router(health_router)

from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from fastapi import Request

# Diccionario de nombres legibles (usa los alias definidos para traducir errores)
FIELD_NAMES = {
    "id": "Identificador",
    "ad_type": "Tipo_de_Anuncio",
    "start_date": "Fecha_de_Inicio",
    "end_date": "Fecha_de_Fin",
    "created_on": "Fecha_de_Creacion",
    "lat": "Latitud",
    "lon": "Longitud",
    "l1": "Ciudad", 
    "l2": "Barrio", 
    "l3": "Sub_barrio", 
    "l4": "Nivel_de_Ubicacion_4",
    "l5": "Nivel_de_Ubicacion_5",
    "l6": "Nivel_de_Ubicacion_6",
    "rooms": "Ambientes",
    "bedrooms": "Dormitorios",
    "bathrooms": "Banios",
    "surface_total": "Superficie_Total_m2",
    "surface_covered": "Superficie_Cubierta_m2",
    "currency": "Moneda",
    "price_period": "Periodo_de_Precio",
    "title": "Titulo_del_Anuncio",
    "description": "Descripcion_del_Anuncio",
    "property_type": "Tipo_de_Propiedad",
    "operation_type": "Tipo_de_Operacion",
    "price": "Precio"
}

# Personalizamos el manejo de errores de validación
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """
    Captura los errores de validación y devuelve los nombres de campos en español
    """
    errors = []
    for err in exc.errors():
        # Extraemos el campo (por ejemplo, 'l1') desde la ruta del error
        field = err.get("loc")[-1] if err.get("loc") else "Campo desconocido"
        # Usamos el mapeo de nombres internos a alias para la traducción
        readable_name = FIELD_NAMES.get(field, field)
        message = err.get("msg", "Error desconocido")
        errors.append(f"Error en el campo '{readable_name}': {message}")

    return JSONResponse(
        status_code=422,
        content={"detail": errors}
    )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)