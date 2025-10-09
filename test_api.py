#!/usr/bin/env python3
"""
Test script for the Property Price Prediction API
"""

import requests
import json

# API base URL
BASE_URL = "http://localhost:8000"

def test_health_check():
    """Test the health check endpoint"""
    response = requests.get(f"{BASE_URL}/")
    print("Health Check Response:")
    print(json.dumps(response.json(), indent=2))
    print()

def test_prediction():
    """Test the prediction endpoint with sample data"""
    
    # Sample property data (matching the schema)
    # Coordenadas de Palermo, Buenos Aires (antes del swap lat/lon)
    sample_property = {
        "id": 1,
        "ad_type": "property",
        "start_date": "2023-01-01",
        "end_date": "2023-12-31", 
        "created_on": "2023-01-01",
        "lat": -58.4200, # latitud de Palermo
        "lon": -34.5900,  # longitud de Palermo 
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
    
    response = requests.post(f"{BASE_URL}/predict", json=sample_property)
    print("Prediction Response:")
    print(json.dumps(response.json(), indent=2))
    print()

def test_invalid_property():
    """Test with invalid property (wrong currency) to see flags"""
    
    invalid_property = {
        "id": 2,
        "ad_type": "property",
        "start_date": "2023-01-01",
        "end_date": "2023-12-31",
        "created_on": "2023-01-01",
        "lat": -34.6037,  # latitud de CABA
        "lon": -58.3816,  # longitud de CABA
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
        "currency": "ARS",  # Invalid currency - should be USD
        "price_period": "monthly",
        "title": "Departamento 2 ambientes 65m2 Palermo",
        "description": "Hermoso departamento de 2 ambientes en Palermo, 65 metros cuadrados",
        "property_type": "Departamento",
        "operation_type": "Venta", 
        "price": 185000.0
    }
    
    response = requests.post(f"{BASE_URL}/predict", json=invalid_property)
    print("Invalid Property Response (should show flags):")
    print(json.dumps(response.json(), indent=2))
    print()

def test_model_info():
    """Test the model info endpoint"""
    response = requests.get(f"{BASE_URL}/model/info")
    print("Model Info Response:")
    print(json.dumps(response.json(), indent=2))
    print()

def test_prediction_with_regex_extraction():
    """Test prediction with title that needs regex extraction for rooms"""
    
    # Property data where rooms is None but title contains room info
    regex_property = {
        "id": 3,
        "ad_type": "property",
        "start_date": "2023-01-01",
        "end_date": "2023-12-31",
        "created_on": "2023-01-01",
        "lat": -34.5875,  # latitud de Villa Crespo
        "lon": -58.4387,  # longitud de Villa Crespo
        "l1": "Argentina",
        "l2": "Capital Federal",
        "l3": "Villa Crespo",
        "l4": None,
        "l5": None,
        "l6": None,
        "rooms": None,  # No rooms specified - should extract from title
        "bedrooms": None,
        "bathrooms": 1.0,
        "surface_total": None,  # No surface specified - should extract from title
        "surface_covered": None,
        "currency": "USD",
        "price_period": "monthly",
        "title": "Hermoso departamento 3 ambientes 80m2 en Villa Crespo",
        "description": "Departamento de tres ambientes con 80 metros cuadrados en Villa Crespo",
        "property_type": "Departamento",
        "operation_type": "Venta",
        "price": 220000.0
    }
    
    response = requests.post(f"{BASE_URL}/predict", json=regex_property)
    print("Prediction with RegEx Extraction Response:")
    print(json.dumps(response.json(), indent=2))
    print()

def test_none_coordinates():
    """Test prediction with None coordinates - should be flagged"""
    
    # Property data with None coordinates
    none_coords_property = {
        "id": 4,
        "ad_type": "property",
        "start_date": "2023-01-01",
        "end_date": "2023-12-31",
        "created_on": "2023-01-01",
        "lat": None,  # No coordinates
        "lon": None,  # No coordinates
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
    
    response = requests.post(f"{BASE_URL}/predict", json=none_coords_property)
    print("None Coordinates Response (should show appropriate flags):")
    if response.status_code == 200:
        print(json.dumps(response.json(), indent=2))
    else:
        print(f"HTTP {response.status_code}: {response.text}")
    print()

if __name__ == "__main__":
    print("Testing Property Price Prediction API")
    print("=" * 50)
    
    try:
        test_health_check()
        test_prediction()
        test_invalid_property()
        test_prediction_with_regex_extraction()
        test_none_coordinates()
        test_model_info()
        
    except requests.exceptions.ConnectionError:
        print("Error: Could not connect to API. Make sure the server is running at http://localhost:8000")
        print("Start the server with: uvicorn app.main:app --reload")
    except Exception as e:
        print(f"Error during testing: {e}")
