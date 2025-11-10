# Mapa conceptual y de seguimiento — Property Price Prediction

**Objetivo:** seguimiento end-to-end del modelo: **entrenar → registrar en MLflow → dockerizar → desplegar API → evaluar en producción**.

---

## 1. Datos & Prepro

- **Input:** `data/raw/properaty_dataset_alumnos.csv`  
- **Preprocess:** `Pipeline/preprocess/{filter_data,regex_extraction,geo_validation,subte_distance,clean_outliers}.py`  
- **Salida:** `data/processed/datos_limpios.csv`

## 2. Entrenamiento & Experimentos

- **Orquestación:** `Pipeline/preprocesamiento.py`, `Pipeline/creacion_experimento.py`  
- **Tracking:** `mlruns/` (parámetros, métricas, artefactos)  
- **Notebook de pruebas:** `Notebooks/XGBoost_testing.ipynb`

## 3. Registro (MLflow Model Registry)

- **Scripts:** `Pipeline/registro_exp_mlflow.py`, `Pipeline/inicializacion_mlflow.py`  
- **Estados:** _Staging_ → _Production_ (gate de calidad)

## 4. Dockerización & Deploy

- **Build:** `Dockerfile` (+ `.dockerignore`)  
- **Servicio:** `app/` (FastAPI: `/health`, `/main`)  
- **Arranque:** `start_api_prueba_docker.sh`

---

## Pipeline como YAML (para README / documentación técnica)

```yaml
pipeline:
  data:
    raw: data/raw/properaty_dataset_alumnos.csv
    processed: data/processed/datos_limpios.csv

  preprocess:
    orchestrator: Pipeline/preprocesamiento.py
    steps:
      - Pipeline/preprocess/filter_data.py
      - Pipeline/preprocess/regex_extraction.py
      - Pipeline/preprocess/geo_validation.py
      - Pipeline/preprocess/subte_distance.py
      - Pipeline/preprocess/clean_outliers.py

  training:
    experiment_script: Pipeline/creacion_experimento.py
    notebooks:
      - Notebooks/XGBoost_testing.ipynb
    tracking:
      mlruns_dir: mlruns/

  registry:
    init: Pipeline/inicializacion_mlflow.py
    register: Pipeline/registro_exp_mlflow.py
    states: [Staging, Production]
    promote_gate:
      perf_delta_min: +0.01   # vs modelo actual
      p95_latency_ms_max: 300
      folds_var_max_pct: X    # completa tu umbral
      reproducible: true

  packaging:
    dockerfile: Dockerfile
    dockerignore: .dockerignore
    app_dir: app/
    health_endpoints: ["/health", "/metrics", "/predict"]
    start_scripts:
      - start_api.sh
      - start_api_prueba_docker.sh
```

---

## Diagrama ASCII 
```
RAW CSV
  └─ data/raw/properaty_dataset_alumnos.csv
          |
          v
PREPROCESS (Pipeline/preprocesamiento.py)
  ├─ filter_data.py
  ├─ regex_extraction.py
  ├─ geo_validation.py
  ├─ subte_distance.py
  └─ clean_outliers.py
          |
          v
PROCESSED CSV
  └─ data/processed/datos_limpios.csv
          |
          v
TRAIN & EXPERIMENTS
  ├─ creacion_experimento.py  -> mlruns/ (params, metrics, artifacts)
  └─ XGBoost_testing.ipynb
          |
          v
MLFLOW REGISTRY
  └─ registro_exp_mlflow.py + inicializacion_mlflow.py
     (Staging -> Production)  [Gate de calidad]
          |
          v
DOCKER IMAGE
  ├─ Dockerfile (+ .dockerignore)
  └─ app/  -> /predict /health /metrics
          |
          v
DEPLOY (start_api.sh / start_api_prueba_docker.sh)
```

---
