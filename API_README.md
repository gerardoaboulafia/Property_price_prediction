# Property Price Prediction API

FastAPI application that exposes the property price prediction pipeline through REST endpoints.

## Setup

1. Make sure you have the required dependencies installed:
```bash
pip install -r requirements.txt
```

2. The API expects the following files to be present:
   - `Pipeline/models/xgb_pipeline2.pkl` - Trained XGBoost model
   - `Pipeline/estaciones-de-subte copy.csv` - Subway stations data
   - `Pipeline/barrios copy.csv` - Neighborhoods geographic data

## Running the API

```bash
# From the project root directory
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

The API will be available at:
- **API**: http://localhost:8000
- **Interactive docs (Swagger)**: http://localhost:8000/docs
- **Alternative docs (ReDoc)**: http://localhost:8000/redoc

## API Endpoints

### Health Check
- **GET** `/` - Returns API status and pipeline information

### Model Information  
- **GET** `/model/info` - Returns information about the loaded model

### Price Prediction
- **POST** `/predict` - Predicts property price from input data

## Input Schema

The `/predict` endpoint accepts JSON with the following structure:

```json
{
  "id": 1,
  "ad_type": "property",
  "start_date": "2023-01-01",
  "end_date": "2023-12-31",
  "created_on": "2023-01-01",
  "lat": -34.6037,
  "lon": -58.3816,
  "l1": "Argentina",
  "l2": "Capital Federal",
  "l3": "Palermo",
  "l4": null,
  "l5": null,
  "l6": null,
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
```

## Output Schema

The prediction response includes:

```json
{
  "predicted_price": 189500.50,
  "preprocessing_flags": null,
  "is_valid_for_prediction": true,
  "input_features": {
    "place_l3": "Palermo",
    "type": "Departamento",
    "rooms_final": 2.0,
    "m2_final": 65.0,
    "distancia_subte_cercano": 0.85
  }
}
```

- **predicted_price**: The predicted price in USD
- **preprocessing_flags**: Any validation errors during preprocessing (null if valid)
- **is_valid_for_prediction**: Boolean indicating if the input passed validation
- **input_features**: The actual features used by the model after preprocessing

## Pipeline Processing Steps

The API applies the same preprocessing pipeline as the notebook:

1. **Filter by Currency and Place**: Validates currency is USD and location is Capital Federal
2. **RegEx Feature Extraction**: Extracts room count and surface area from title/description
3. **Geographic Validation**: Validates coordinates are within Buenos Aires boundaries
4. **Subway Distance Calculation**: Calculates distance to nearest subway station
5. **Outlier Cleaning**: Flags and handles outliers in price, rooms, and surface area

## Testing

Use the provided test script to validate the API:

```bash
python test_api.py
```

This will test:
- Health check endpoint
- Valid property prediction
- Invalid property handling (shows flags)
- Model information retrieval

## Example Usage with curl

```bash
# Health check
curl -X GET "http://localhost:8000/"

# Predict price
curl -X POST "http://localhost:8000/predict" \
  -H "Content-Type: application/json" \
  -d '{
    "id": 1,
    "ad_type": "property",
    "start_date": "2023-01-01",
    "end_date": "2023-12-31",
    "created_on": "2023-01-01",
    "lat": -34.6037,
    "lon": -58.3816,
    "l1": "Argentina",
    "l2": "Capital Federal",
    "l3": "Palermo",
    "l4": null,
    "l5": null,
    "l6": null,
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
  }'
```

## Notes

- The API handles coordinate swapping (lat/lon) internally as done in the original notebook
- All column transformations and feature engineering from the notebook are preserved
- Invalid properties (wrong currency, location, outliers) return appropriate flags instead of predictions
- The API uses the same XGBoost model trained in your pipeline
