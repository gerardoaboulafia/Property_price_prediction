import mlflow
import mlflow.sklearn
import pandas as pd
import pickle
from xgboost import XGBRegressor
from sklearn.metrics import mean_squared_error, r2_score
import numpy as np
from preprocess.db_utils import get_connection, download_from_mysql

# 1. Cargar datos limpios desde SQL
def load_clean_data():
    conn = get_connection(
        user="labo_ame_agus", 
        password="ameagusmica", 
        host="172.29.208.1", 
        port=3307, 
        database="laboratorioII"
    )
    data = download_from_mysql("processed_data", conn)
    conn.close()
    return data

# 2. Extraer hiperparámetros desde el .pkl
def get_params_from_pkl(path="Pipeline/models/xgboost_property_model3.pkl"):
    with open(path, "rb") as f:
        model_pkl = pickle.load(f)
    if hasattr(model_pkl, "get_params"):
        return model_pkl.get_params()
    else:
        raise ValueError("El archivo .pkl no contiene un modelo sklearn-compatible.")

# 3. Preparar features
def prepare_features(df, target="price"):
    # Filtrar filas con NaN en la columna target
    df = df.dropna(subset=[target]).copy()

    # Asegurar que el target sea numérico
    df[target] = pd.to_numeric(df[target], errors="coerce")

    # Eliminar filas con NaN o inf en target
    df = df[np.isfinite(df[target])]

    # Separar X e y
    X = df.drop(columns=[target])
    y = df[target]

    # Asegurar que las numéricas sean float
    for col in ["rooms_final", "m2_final", "distancia_subte_cercano"]:
        X[col] = pd.to_numeric(X[col], errors="coerce")

    # Variables categóricas
    for col in ["l2", "property_type", "flag"]:
        if col in X.columns:
            X[col] = X[col].astype("category")

    # Dropear cualquier fila con NaN en X después de la conversión
    X = X.dropna()
    y = y.loc[X.index]

    return X, y


# 4. Entrenar modelo con los hiperparámetros del pkl
def train_new_model(X, y, params):
    # Filtrar solo los parámetros relevantes que XGBRegressor acepta
    allowed_params = XGBRegressor().get_params().keys()
    clean_params = {k: v for k, v in params.items() if k in allowed_params}

    model = XGBRegressor(**clean_params)
    model.fit(X, y)

    preds = model.predict(X)
    rmse = np.sqrt(mean_squared_error(y, preds))
    r2 = r2_score(y, preds)

    return model, rmse, r2

# 5. Loggear en MLflow
def log_with_mlflow(model, rmse, r2):
    mlflow.set_tracking_uri("http://localhost:5000")
    mlflow.set_experiment("xgboost_models")

    with mlflow.start_run(run_name="xgboost_retrained_with_pkl_params"):
        # Guardar hiperparámetros
        for k, v in model.get_params().items():
            mlflow.log_param(k, v)

        # Métricas
        mlflow.log_metric("rmse", rmse)
        mlflow.log_metric("r2", r2)

        # Guardar el modelo
        mlflow.sklearn.log_model(model, artifact_path="model")

        print(f"Modelo reentrenado loggeado en MLflow con RMSE={rmse:.2f}, R2={r2:.2f}")

if __name__ == "__main__":
    data = load_clean_data()
    params = get_params_from_pkl()
    X, y = prepare_features(data)
    model, rmse, r2 = train_new_model(X, y, params)
    log_with_mlflow(model, rmse, r2)
