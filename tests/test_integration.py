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
    "Nivel_de_Ubicacion_4": "",
    "Nivel_de_Ubicacion_5": "",
    "Nivel_de_Ubicacion_6": 0,
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


    response = client.post("/predict", json=payload)

    # Verifica código HTTP
    assert response.status_code == 200, f"Error en respuesta: {response.text}"

    # Verifica contenido JSON
    data = response.json()
    assert "predicted_price" in data, "La respuesta no contiene 'predicted_price'"
    assert isinstance(data["predicted_price"], (int, float)), "El valor no es numérico"


#para que corra este test hay que correr: pytest -v tests/test_integration.py
#en la terminal!!!!
