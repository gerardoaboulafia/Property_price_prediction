import mlflow
import mlflow.sklearn
import pandas as pd
import pickle
from sqlalchemy import create_engine
from sklearn.metrics import mean_squared_error, r2_score
import numpy as np
from preprocess.db_utils import get_connection, download_from_mysql

# 1. Conectar a la base de datos para traer los datos limpios

def load_clean_data():
    # 1. Conexión con las credenciales del equipo
    conn = get_connection(
        user="labo_ame_agus", 
        password="ameagusmica", 
        host="172.29.208.1", 
        port=3307, 
        database="laboratorioII"
    )

    # 2. Descargar dataset desde MySQL
    data = download_from_mysql("processed_data", conn)

    # 3. Cerrar la conexión
    conn.close()

    return data


# 2. Cargar modelo entrenado desde un archivo .pkl
def load_model_from_pkl(path="xgboost_property_model3.pkl"):
    with open(path, "rb") as f:
        model = pickle.load(f)
    return model

# 3. Evaluar el modelo con los datos actuales de SQL
def evaluate_model(model, data):
    X = data.drop(columns=["price"])   # Ajustar si el target es "price"
    y = data["price"]

    preds = model.predict(X)

    rmse = np.sqrt(mean_squared_error(y, preds))
    r2 = r2_score(y, preds)

    return rmse, r2

# 4. Loggear en MLflow
def log_with_mlflow(model, rmse, r2):
    mlflow.set_tracking_uri("http://localhost:5000")
    mlflow.set_experiment("xgboost_models")

    with mlflow.start_run(run_name="xgboost_model_from_pkl"):
        # Log de parámetros principales (si están en el modelo)
        if hasattr(model, "get_params"):
            params = model.get_params()
            for k, v in params.items():
                mlflow.log_param(k, v)

        # Log de métricas
        mlflow.log_metric("rmse", rmse)
        mlflow.log_metric("r2", r2)

        # Guardar el modelo como artefacto
        mlflow.sklearn.log_model(model, artifact_path="model")

        print(f"Modelo cargado desde .pkl loggeado en MLflow con RMSE={rmse:.2f} y R2={r2:.2f}")

if __name__ == "__main__":
    data = load_clean_data()
    model = load_model_from_pkl("xgboost_property_model3.pkl")
    rmse, r2 = evaluate_model(model, data)
    log_with_mlflow(model, rmse, r2)
