from locust import HttpUser, task, between

class PropertyAPITest(HttpUser):
    wait_time = between(1, 5)  # segundos entre requests

    @task
    def predict_price(self):
        payload = {
            "id": 1,
            "ad_type": "property",
            "start_date": "2023-01-01",
            "end_date": "2023-12-31",
            "created_on": "2023-01-01",
            "lat": -34.59,
            "lon": -58.42,
            "l1": "Argentina",
            "l2": "Capital Federal",
            "l3": "Palermo",
            "rooms": 2,
            "bedrooms": 1,
            "bathrooms": 1,
            "surface_total": 65,
            "surface_covered": 60,
            "currency": "USD",
            "price_period": "monthly",
            "title": "Departamento 2 ambientes",
            "description": "Hermoso departamento en Palermo",
            "property_type": "Departamento",
            "operation_type": "Venta",
            "price": 185000
        }
        self.client.post("/predict", json=payload)
