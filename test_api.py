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
    response = requests.get(f"{BASE_URL}/health")
    print("Health Check Response:")
    print(json.dumps(response.json(), indent=2))
    print()

def test_prediction():
    """Test the prediction endpoint with sample data"""
    
    # Sample property data (matching the schema)
    # Coordenadas de Palermo, Buenos Aires (antes del swap lat/lon)
    sample_property = {
        "Identificador": 1,
        "Tipo_de_Anuncio": "property",
        "Fecha_de_Inicio": "2023-01-01",
        "Fecha_de_Fin": "2023-12-31", 
        "Fecha_de_Creacion": "2023-01-01",
        "Latitud": -34.6037,
        "Longitud": -58.3816,
        "Ciudad": "Capital Federal",
        "Barrio": "Palermo",
        "Sub_barrio": "Palermo Soho",
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
    
    response = requests.post(f"{BASE_URL}/predict", json=sample_property)
    print("Prediction Response:")
    try:
        print(json.dumps(response.json(), indent=2))
    except Exception as e:
        print(f"Error decoding JSON: {e}")
        print(f"Response status: {response.status_code}")
        print(f"Response text:\n{response.text}")

    print()

def test_invalid_property():
    """Test with invalid property (wrong currency) to see flags"""
    
    invalid_property = {
        "Identificador": 2,
        "Tipo_de_Anuncio": "property",
        "Fecha_de_Inicio": "2023-01-01",
        "Fecha_de_Fin": "2023-12-31",
        "Fecha_de_Creacion": "2023-01-01",
        "Latitud": -34.6037,
        "Longitud": -58.3816,
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
        "Moneda": "ARS",
        "Periodo_de_Precio": "monthly",
        "Titulo_del_Anuncio": "Departamento 2 ambientes 65m2 Palermo",
        "Descripcion_del_Anuncio": "Hermoso departamento de 2 ambientes en Palermo, 65 metros cuadrados",
        "Tipo_de_Propiedad": "Departamento",
        "Tipo_de_Operacion": "Venta", 
        "Precio": 185000.0
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
        "Identificador": 3,
        "Tipo_de_Anuncio": "property",
        "Fecha_de_Inicio": "2023-01-01",
        "Fecha_de_Fin": "2023-12-31",
        "Fecha_de_Creacion": "2023-01-01",
        "Latitud": -34.5875,
        "Longitud": -58.4387,
        "Ciudad": "Capital Federal",
        "Barrio": "Villa Crespo",
        "Sub_barrio": "Villa Crespo",
        "Nivel_de_Ubicacion_4": None,
        "Nivel_de_Ubicacion_5": None,
        "Nivel_de_Ubicacion_6": None,
        "Ambientes": None,
        "Dormitorios": None,
        "Banios": 1.0,
        "Superficie_Total_m2": None,
        "Superficie_Cubierta_m2": None,
        "Moneda": "USD",
        "Periodo_de_Precio": "monthly",
        "Titulo_del_Anuncio": "Hermoso departamento 3 ambientes 80m2 en Villa Crespo",
        "Descripcion_del_Anuncio": "Departamento de tres ambientes con 80 metros cuadrados en Villa Crespo",
        "Tipo_de_Propiedad": "Departamento",
        "Tipo_de_Operacion": "Venta",
        "Precio": 220000.0
    }
    
    response = requests.post(f"{BASE_URL}/predict", json=regex_property)
    print("Prediction with RegEx Extraction Response:")
    print(json.dumps(response.json(), indent=2))
    print()

def test_none_coordinates():
    """Test prediction with None coordinates - should be flagged"""
    
    # Property data with None coordinates
    none_coords_property = {
        "Identificador": 4,
        "Tipo_de_Anuncio": "property",
        "Fecha_de_Inicio": "2023-01-01",
        "Fecha_de_Fin": "2023-12-31",
        "Fecha_de_Creacion": "2023-01-01",
        "Latitud": None,
        "Longitud": None,
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