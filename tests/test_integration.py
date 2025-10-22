from fastapi.testclient import TestClient
import sys, os

# Agregar el path raíz
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Importar la app principal
from app.main import app

client = TestClient(app)

def test_api_prediction_success():
    """Verifica que la API procese correctamente una solicitud de predicción."""
    payload = {
    "id": 1,
    "ad_type": "property",
    "start_date": "2023-01-01",
    "end_date": "2023-12-31", 
    "created_on": "2023-01-01",
    "lat": -34.6037,
    "lon": -58.3816,
    "l1": "Capital Federal",
    "l2": "Palermo",
    "l3": "Palermo Soho",
    "rooms": 3.0,
    "surface_total": 80.0,
    "currency": "USD",
    "price_period": "monthly",
    "title": "Departamento 3 ambientes Palermo",
    "description": "Hermoso departamento de 3 ambientes en Palermo",
    "property_type": "Departamento",
    "operation_type": "Venta",
    "price": 180000.0
}


    response = client.post("/predict", json=payload)

    # Verifica código HTTP
    assert response.status_code == 200, f"Error en respuesta: {response.text}"

    # Verifica contenido JSON
    data = response.json()
    assert "predicted_price" in data, "La respuesta no contiene 'predicted_price'"
    assert isinstance(data["predicted_price"], (int, float)), "El valor no es numérico"




#para que corra este test hay que correr: pytest -v tests/test_integration.py
#en la terminal!!!!
