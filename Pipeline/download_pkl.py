import mlflow
import joblib

# Ruta del modelo en MLflow
model_name = "modelo_api_p"
model_version = 1  # o "latest"

# Cargar modelo registrado
model_uri = f"models:/{model_name}/{model_version}"
model = mlflow.sklearn.load_model(model_uri)

# Guardar como pkl en tu carpeta Pipeline/models
output_path = "Pipeline/models/xgb_prueba_api.pkl"
joblib.dump(model, output_path)

print(f"Modelo guardado en {output_path}")
