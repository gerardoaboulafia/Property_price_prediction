from locust import HttpUser, task, between

class PropertyAPITest(HttpUser):
    wait_time = between(1, 5)  # segundos entre requests

    @task
    def predict_price(self):
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
        "Nivel_de_Ubicacion_6": "",
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
        self.client.post("/predict", json=payload)
