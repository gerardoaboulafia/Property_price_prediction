# Stress Test – Property Price Prediction API

## Requisitos
* pip install locust
* API de Property Price Prediction levantada en http://localhost:8000

## 1- Levantar la API
Levantar la api a través del powershell:

`uvicorn app.main:app --reload --host 0.0.0.0 --port 8000`

--reload permite recargar cambios automáticamente.

## 2- Correr el stress test
En una nueva terminal correr:

`locust -f tests\stress_test.py --host=http://localhost:8000`

Abrir navegador en `http://localhost:8089`

Configurar:

* Number of users: 20
* Spawn rate: 2
* Run time: 2m (opcional)

Presionar **Start swarming**

Revisar métricas: 
* requests 
* fallos 
* tiempo promedio 
* RPS

