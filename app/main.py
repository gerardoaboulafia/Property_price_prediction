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

try:
    model = joblib.load(MODEL_PATH)
    print(f"Model loaded successfully from {MODEL_PATH}")
except Exception as e:
    print(f"Error loading model: {e}")
    model = None

class PropertyInput(BaseModel):
    """Input schema matching the original dataset structure"""
    id: int = Field(..., description="Unique identifier for the property")
    ad_type: str = Field(..., description="Type of advertisement")
    start_date: str = Field(..., description="Start date of the listing")
    end_date: str = Field(..., description="End date of the listing")
    created_on: str = Field(..., description="Date when the listing was created")
    lat: Optional[float] = Field(None, description="Latitude coordinate")
    lon: Optional[float] = Field(None, description="Longitude coordinate")
    l1: str = Field(..., description="Location level 1 (country)")
    l2: str = Field(..., description="Location level 2 (province/state)")
    l3: str = Field(..., description="Location level 3 (city/neighborhood)")
    l4: Optional[str] = Field(None, description="Location level 4")
    l5: Optional[str] = Field(None, description="Location level 5")
    l6: Optional[float] = Field(None, description="Location level 6")
    rooms: Optional[float] = Field(None, description="Number of rooms")
    bedrooms: Optional[float] = Field(None, description="Number of bedrooms")
    bathrooms: Optional[float] = Field(None, description="Number of bathrooms")
    surface_total: Optional[float] = Field(None, description="Total surface area in m²")
    surface_covered: Optional[float] = Field(None, description="Covered surface area in m²")
    currency: str = Field(..., description="Currency of the price (e.g., USD)")
    price_period: str = Field(..., description="Price period (e.g., monthly)")
    title: str = Field(..., description="Property listing title")
    description: str = Field(..., description="Property description")
    property_type: str = Field(..., description="Type of property (e.g., Departamento, Casa, PH)")
    operation_type: str = Field(..., description="Type of operation (e.g., sale, rent)")
    price: float = Field(..., description="Price of the property")

    class Config:
        schema_extra = {
            "example": {
                "id": 1,
                "ad_type": "property",
                "start_date": "2023-01-01",
                "end_date": "2023-12-31",
                "created_on": "2023-01-01",
                "lat": -58.4200,  # Coordenadas conocidas de Palermo (será lon después del swap)
                "lon": -34.5900,  # (será lat después del swap)
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
    #if not (pd.isna(data['lat'].iloc[0]) or pd.isna(data['lon'].iloc[0])):
    #    data = data.rename(columns={'lat': 'temp_lat', 'lon': 'lat'})
    #    data = data.rename(columns={'temp_lat': 'lon'})
    
    # 1. Filter by currency and place
    data = filter_by_currency_place(data)
    
    # 2. Extract features using RegEx
    data = extract_features_regex(data)
    
    # 3. Validate geography
    data = validate_geo(data)
    
    # 4. Calculate distance to nearest subway station
    data = calculate_subte_distance(data, str(SUBTE_STATIONS_PATH))
    
    # 5. Keep only relevant columns (as in notebook)
    data = data[['rooms_final', 'm2_final', 'distancia_subte_cercano', 'l2', 'property_type', 'price', 'flag']]
    
    # 6. Clean outliers
    data = clean_data_outliers(data)
    
    return data

@app.get("/", response_model=PipelineStatus)
async def health_check():
    """Health check endpoint"""
    return PipelineStatus(
        status="healthy",
        model_loaded=model is not None,
        pipeline_components=[
            "filter_by_currency_place",
            "extract_features_regex", 
            "validate_geo",
            "calculate_subte_distance",
            "clean_data_outliers"
        ]
    )

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
        X_features = valid_data.drop(columns=['price', 'flag'])
        
        # Rename columns to match model expectations
        X_features = X_features.rename(columns={
            'l3': 'place_l3',
            'property_type': 'type'
        })
        
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
            "expected_features": ["place_l3", "type", "rooms_final", "m2_final", "distancia_subte_cercano"]
        }
        
        # If it's a pipeline, try to get more details
        if hasattr(model, 'steps'):
            info["pipeline_steps"] = [step[0] for step in model.steps]
            
        return info
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting model info: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
