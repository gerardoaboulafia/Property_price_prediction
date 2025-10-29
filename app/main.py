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

class PropertyInput(BaseModel):
    id: int = Field(..., title="Identificador", description="Identificador único del inmueble")
    ad_type: str = Field(..., title="Tipo de anuncio")
    start_date: str = Field(..., title="Fecha de inicio")
    end_date: str = Field(..., title="Fecha de fin")
    created_on: str = Field(..., title="Fecha de creación")
    lat: Optional[float] = Field(None, title="Latitud")
    lon: Optional[float] = Field(None, title="Longitud")
    l1: str = Field(..., title="Ciudad")        # 👈 aparece así en Swagger
    l2: str = Field(..., title="Barrio")        # 👈 aparece así en Swagger
    l3: Optional[str] = Field(None, title="Sub-barrio")  # 👈 opcional
    rooms: Optional[float] = Field(None, title="Cantidad de ambientes")
    bedrooms: Optional[float] = Field(None, title="Cantidad de dormitorios")
    bathrooms: Optional[float] = Field(None, title="Cantidad de baños")
    surface_total: Optional[float] = Field(None, title="Superficie total (m²)")
    surface_covered: Optional[float] = Field(None, title="Superficie cubierta (m²)")
    currency: str = Field(..., title="Moneda")
    price_period: str = Field(..., title="Periodo de precio")
    title: str = Field(..., title="Título")
    description: str = Field(..., title="Descripción")
    property_type: str = Field(..., title="Tipo de propiedad")
    operation_type: str = Field(..., title="Tipo de operación")
    price: float = Field(..., title="Precio")


    class Config:
        schema_extra = {
            "example": {
                "id": 1,
                "ad_type": "property",
                "start_date": "2023-01-01",
                "end_date": "2023-12-31",
                "created_on": "2023-01-01",
                "lat": -34.5900,  # Coordenadas conocidas de Palermo (será lon después del swap)
                "lon": -58.4200,  # (será lat después del swap)
                "l1": "Argentina",
                "l2": "Capital Federal",
                "l3": "Palermo",
                "l4": None,
                "l5": None,
                "l6": None,
                "rooms": 2.0,
                "bedrooms": 1.0,
                "bathrooms": 1.0,
                "surface_total": 65.0,
                "surface_covered": 60.0,
                "currency": "USD",
                "price_period": "monthly",
                "title": "Departamento 2 ambientes 65m2 Palermo",
                "description": "Hermoso departamento de 2 ambientes en Palermo, 65 metros cuadrados",
                "property_type": "Departamento",
                "operation_type": "Venta",
                "price": 185000.0
            }
        }

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

def preprocess_data(property_data: PropertyInput) -> pd.DataFrame:
    """
    Process the input data through the same pipeline as the notebook
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
    
    # Apply the same transformations as in the notebook
    # IMPORTANT: Swap lat and lon (exactly as in notebook) - but only if both are not None
    # Verificar coordenadas antes de hacer el swap
    #print(f"Antes del intercambio: lat = {data['lat'].iloc[0]}, lon = {data['lon'].iloc[0]}")

    # Swap lat and lon (solo si ambas están presentes)
    #if not (pd.isna(data['lat'].iloc[0]) or pd.isna(data['lon'].iloc[0])):
    #    data = data.rename(columns={'lat': 'temp_lat', 'lon': 'lat'})
    #    data = data.rename(columns={'temp_lat': 'lon'})


    # Verificar coordenadas después del swap
    #print(f"Después del intercambio: lat = {data['lat'].iloc[0]}, lon = {data['lon'].iloc[0]}")

    
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

# @app.get("/", response_model=PipelineStatus)
# async def health_check():
#     """Health check endpoint"""
#     return PipelineStatus(
#         status="healthy",
#         model_loaded=model is not None,
#         pipeline_components=[
#             "filter_by_currency_place",
#             "extract_features_regex", 
#             "validate_geo",
#             "calculate_subte_distance",
#             "clean_data_outliers"
#         ]
#     )

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

        
        # Rename columns to match model expectations
        #X_features = X_features.rename(columns={
        #    'l3': 'place_l3',
        #    'property_type': 'type'
        #})

        
        
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
            "model_type": type(model).__name__,
            "model_path": str(MODEL_PATH),
            "expected_features": ['rooms_final', 'm2_final', 'distancia_subte_cercano', 'l2', 'property_type', 'price', 'flag']
        }
        
        # If it's a pipeline, try to get more details
        if hasattr(model, 'steps'):
            info["pipeline_steps"] = [step[0] for step in model.steps]
            
        return info
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting model info: {str(e)}")

from app.health import router as health_router
app.include_router(health_router)

from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from fastapi import Request

# Diccionario de nombres legibles
FIELD_NAMES = {
    "id": "Identificador",
    "ad_type": "Tipo de anuncio",
    "start_date": "Fecha de inicio",
    "end_date": "Fecha de fin",
    "created_on": "Fecha de creación",
    "lat": "Latitud",
    "lon": "Longitud",
    "l1": "Ciudad",         # actualizado
    "l2": "Barrio",         # actualizado
    "l3": "Sub-barrio",     # actualizado
    "rooms": "Cantidad de ambientes",
    "bedrooms": "Cantidad de dormitorios",
    "bathrooms": "Cantidad de baños",
    "surface_total": "Superficie total (m²)",
    "surface_covered": "Superficie cubierta (m²)",
    "currency": "Moneda",
    "price_period": "Periodo de precio",
    "title": "Título",
    "description": "Descripción",
    "property_type": "Tipo de propiedad",
    "operation_type": "Tipo de operación",
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
