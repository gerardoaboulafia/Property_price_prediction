from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from pydantic import BaseModel, Field
from typing import Optional, List
import pandas as pd
import numpy as np
import sys
import os
import joblib
from pathlib import Path

# === Agregar carpeta Pipeline al path ===
pipeline_dir = Path(__file__).parent.parent / "Pipeline"
sys.path.append(str(pipeline_dir))

# === Importar funciones de preprocesamiento ===
from preprocess.filter_data import filter_by_currency_place
from preprocess.regex_extraction import extract_features_regex
from preprocess.geo_validation import validate_geo
from preprocess.subte_distance import calculate_subte_distance
from preprocess.clean_outliers import clean_data_outliers

# === Inicializar FastAPI ===
app = FastAPI(
    title="Property Price Prediction API",
    description="API para predecir precios inmobiliarios eligiendo el modelo con mayor R² automáticamente",
    version="2.0.0"
)

# === Rutas de archivos ===
MODELS_DIR = pipeline_dir / "models"
SUBTE_STATIONS_PATH = pipeline_dir / "estaciones-de-subte copy.csv"
BARRIOS_CSV_PATH = pipeline_dir / "barrios copy.csv"

# === Buscar el modelo con mejor R² ===
def load_best_model_by_r2(models_dir: Path):
    """Carga el modelo con el mayor valor de R² registrado."""
    best_model = None
    best_r2 = -np.inf
    best_model_path = None

    if not models_dir.exists():
        raise FileNotFoundError(f"No se encontró el directorio de modelos: {models_dir}")

    for file in models_dir.glob("*.pkl"):
        try:
            data = joblib.load(file)
            if isinstance(data, dict) and "model" in data and "r2" in data:
                r2 = data["r2"]
                if r2 > best_r2:
                    best_r2 = r2
                    best_model = data["model"]
                    best_model_path = file
        except Exception as e:
            print(f"No se pudo leer {file.name}: {e}")

    if best_model is None:
        raise ValueError("No se encontró ningún modelo válido con R² registrado.")

    print(f"✅ Modelo cargado: {best_model_path.name} (R² = {best_r2:.4f})")
    return best_model, best_r2, best_model_path

# === Cargar modelo con mejor R² ===
try:
    model, best_r2, best_model_path = load_best_model_by_r2(MODELS_DIR)
except Exception as e:
    print(f"⚠️ Error al cargar el mejor modelo: {e}")
    model, best_r2, best_model_path = None, None, None


# === SCHEMAS DE ENTRADA Y SALIDA ===

class PropertyInput(BaseModel):
    id: int = Field(..., alias="Identificador")
    ad_type: str = Field(..., alias="Tipo_de_Anuncio")
    start_date: str = Field(..., alias="Fecha_de_Inicio")
    end_date: str = Field(..., alias="Fecha_de_Fin")
    created_on: str = Field(..., alias="Fecha_de_Creacion")
    lat: Optional[float] = Field(None, alias="Latitud")
    lon: Optional[float] = Field(None, alias="Longitud")
    l1: str = Field(..., alias="Ciudad")
    l2: str = Field(..., alias="Barrio")
    l3: str = Field(..., alias="Sub_barrio")
    l4: Optional[str] = Field(None, alias="Nivel_de_Ubicacion_4")
    l5: Optional[str] = Field(None, alias="Nivel_de_Ubicacion_5")
    l6: Optional[float] = Field(None, alias="Nivel_de_Ubicacion_6")
    rooms: Optional[float] = Field(None, alias="Ambientes")
    bedrooms: Optional[float] = Field(None, alias="Dormitorios")
    bathrooms: Optional[float] = Field(None, alias="Banios")
    surface_total: Optional[float] = Field(None, alias="Superficie_Total_m2")
    surface_covered: Optional[float] = Field(None, alias="Superficie_Cubierta_m2")
    currency: str = Field(..., alias="Moneda")
    price_period: str = Field(..., alias="Periodo_de_Precio")
    title: str = Field(..., alias="Titulo_del_Anuncio")
    description: str = Field(..., alias="Descripcion_del_Anuncio")
    property_type: str = Field(..., alias="Tipo_de_Propiedad")
    operation_type: str = Field(..., alias="Tipo_de_Operacion")
    price: float = Field(..., alias="Precio")

    class Config:
        allow_population_by_field_name = True
        by_alias = True


class PredictionOutput(BaseModel):
    predicted_price: float
    preprocessing_flags: Optional[str]
    is_valid_for_prediction: bool
    input_features: dict


class PipelineStatus(BaseModel):
    status: str
    model_loaded: bool
    best_model_path: Optional[str]
    best_r2: Optional[float]


# === FUNCIONES AUXILIARES ===

def preprocess_data(property_data: PropertyInput) -> pd.DataFrame:
    """Pipeline de preprocesamiento."""
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

    data = filter_by_currency_place(data)
    data = extract_features_regex(data)
    data = validate_geo(data, str(BARRIOS_CSV_PATH))
    data = calculate_subte_distance(data, str(SUBTE_STATIONS_PATH))
    data = data[['rooms_final', 'm2_final', 'distancia_subte_cercano', 'l2', 'property_type', 'price', 'flag']]
    data = clean_data_outliers(data)
    return data


# === ENDPOINTS ===

@app.post("/predict", response_model=PredictionOutput)
async def predict_price(property_data: PropertyInput):
    """Predice el precio de una propiedad usando el mejor modelo (mayor R²)."""
    if model is None:
        raise HTTPException(status_code=500, detail="No hay modelos válidos cargados.")

    try:
        processed = preprocess_data(property_data)
        is_valid = processed['flag'].isnull().iloc[0]
        if not is_valid:
            return PredictionOutput(
                predicted_price=0.0,
                preprocessing_flags=str(processed['flag'].iloc[0]),
                is_valid_for_prediction=False,
                input_features={}
            )

        X = processed.drop(columns=['price'])
        for c in ["rooms_final", "m2_final", "distancia_subte_cercano"]:
            X[c] = pd.to_numeric(X[c], errors="coerce").fillna(0)

        for c in ["l2", "property_type"]:
            X[c] = X[c].fillna("None").astype("category")

        pred = model.predict(X)[0]
        return PredictionOutput(
            predicted_price=float(pred),
            preprocessing_flags=None,
            is_valid_for_prediction=True,
            input_features=X.iloc[0].to_dict()
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error durante la predicción: {e}")


@app.get("/model/info", response_model=PipelineStatus)
async def model_info():
    """Devuelve información sobre el modelo con mejor R²."""
    if model is None:
        raise HTTPException(status_code=500, detail="No hay modelos cargados.")
    return PipelineStatus(
        status="OK",
        model_loaded=True,
        best_model_path=str(best_model_path),
        best_r2=best_r2
    )


# === ERRORES PERSONALIZADOS ===

FIELD_NAMES = {
    "l1": "Ciudad",
    "l2": "Barrio",
    "l3": "Sub_barrio",
    "rooms": "Ambientes",
    "price": "Precio",
    "surface_total": "Superficie_Total_m2",
}

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    errors = []
    for err in exc.errors():
        field = err.get("loc")[-1] if err.get("loc") else "Campo desconocido"
        readable = FIELD_NAMES.get(field, field)
        msg = err.get("msg", "Error desconocido")
        errors.append(f"Error en '{readable}': {msg}")
    return JSONResponse(status_code=422, content={"detail": errors})


# === EJECUCIÓN LOCAL ===
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
