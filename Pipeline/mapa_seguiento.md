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
- **Servicio:** `app/` (FastAPI: `/predict`, `/health`, `/metrics`)  
- **Arranque:** `start_api.sh`, `start_api_prueba_docker.sh`

## 5. Monitoreo & Evaluación en Producción

- **Operativas:** latencia p95, error_rate, disponibilidad, healthchecks  
- **De modelo:** distribución de features, score drift, outliers  
- **Estrategia:** _shadow_/_canary_, comparación con el modelo actual

## 6. Gate de Promoción (ejemplo)

- AUC/F1 nuevo ≥ actual + **0.01**  
- p95 de inferencia ≤ **300 ms**  
- Varianza entre _folds_ ≤ **X%**  
- Recursos dentro de límites; ejecución reproducible (datos + código + params)

## 7. Alertas & Runbook

- **Alertas:** `error_rate > 2% 5m`, `p95 > 500ms 5m`, `health fail 3/5`, `drift > umbral`  
- **Runbook (resumen):** revisar panel → logs → probar `/health` y `/predict` → **rollback** → ticket → plan de reentrenamiento

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

  production_eval:
    operational_metrics: [availability, error_rate, latency_p95]
    model_metrics: [feature_distribution, score_drift, outliers_rate]
    strategies: [shadow, canary]

  alerts:
    - name: high_error_rate
      rule: error_rate > 0.02 for 5m
    - name: high_latency
      rule: latency_p95 > 500ms for 5m
    - name: healthcheck_fails
      rule: health_fail >= 3 of 5
    - name: model_drift
      rule: drift > threshold

  runbook:
    steps:
      - "Revisar panel últimos 15m (latencias/errores)."
      - "Inspeccionar logs (docker/kubectl)."
      - "Probar /health y /predict interno."
      - "Si hubo deploy reciente → rollback al tag anterior."
      - "Abrir ticket y documentar causa raíz."
      - "Plan de reentrenamiento si hay drift."
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
          |
          v
PRODUCCIÓN
  ├─ Monitoreo: latencia p95, error_rate, disponibilidad
  ├─ Modelo: drift, outliers, dist. features
  ├─ Shadow/Canary y comparación
  └─ Alertas -> Runbook -> (Rollback o Reentrenar)
```

---
