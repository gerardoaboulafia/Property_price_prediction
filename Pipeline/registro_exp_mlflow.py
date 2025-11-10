import os
import logging
import pickle
from datetime import datetime
import mlflow
import mlflow.sklearn
import pandas as pd
import numpy as np
from xgboost import XGBRegressor
from sklearn.metrics import mean_squared_error, r2_score
from sklearn.model_selection import train_test_split
import random
from preprocess.db_utils import get_connection, download_from_mysql

# -------------------------------------------------------------------
# CONFIGURACIÓN DE LOGGING
# -------------------------------------------------------------------
log_dir = "Pipeline/logs"
os.makedirs(log_dir, exist_ok=True)
log_path = os.path.join(log_dir, "training_run.log")

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler(log_path, mode="a"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# -------------------------------------------------------------------
# 1. Cargar datos limpios desde SQL
# -------------------------------------------------------------------
def load_clean_data():
    try:
        conn = get_connection(
            user="labo_ame_agus",
            password="ameagusmica",
            host="localhost",
            port=3307,
            database="laboratorioII"
        )
        data = download_from_mysql("processed_data", conn)
        conn.close()
        logger.info("Datos cargados exitosamente desde MySQL.")
        return data
    except Exception as e:
        logger.exception("Error al cargar los datos desde MySQL.")
        raise e

# -------------------------------------------------------------------
# 2. Generar hiperparámetros aleatorios
# -------------------------------------------------------------------
def get_random_params():
    params = {
        'objective': 'reg:squarederror',
        'eval_metric': 'rmse',
        'learning_rate': random.choice([0.01, 0.03, 0.05, 0.07, 0.1]),
        'max_depth': random.choice([3, 4, 5, 6, 7, 8]),
        'n_estimators': random.choice([300, 500, 800, 1000, 1500, 2000]),
        'subsample': random.choice([0.6, 0.7, 0.8, 0.9, 1.0]),
        'colsample_bytree': random.choice([0.6, 0.7, 0.8, 0.9, 1.0]),
        'reg_alpha': random.choice([0, 0.05, 0.1, 0.2, 0.5]),
        'reg_lambda': random.choice([0.5, 0.8, 1, 1.2, 1.5]),
        'random_state': random.randint(1, 100),
        'tree_method': 'hist',
        'enable_categorical': True
    }
    return params

# -------------------------------------------------------------------
# 3. Preparar features
# -------------------------------------------------------------------
def prepare_features(df, target="price"):
    try:
        df = df[df["flag"] == "None"].copy()
        df = df.dropna(subset=[target]).copy()
        df[target] = pd.to_numeric(df[target], errors="coerce")
        df = df[np.isfinite(df[target])]

        X = df.drop(columns=[target])
        y = df[target]

        for col in ["rooms_final", "m2_final", "distancia_subte_cercano"]:
            if col in X.columns:
                X[col] = pd.to_numeric(X[col], errors="coerce")

        for col in ["l2", "property_type", "flag"]:
            if col in X.columns:
                X[col] = X[col].astype("category")

        logger.info(f"Shape de X: {X.shape}, Shape de y: {y.shape}")
        return X, y
    except Exception as e:
        logger.exception("Error durante la preparación de las features.")
        raise e

# -------------------------------------------------------------------
# 4. Entrenar modelo con los hiperparámetros
# -------------------------------------------------------------------
def train_new_model(X, y, params, model_name="xgboost_model"):
    try:
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.3, random_state=42)

        allowed_params = XGBRegressor().get_params().keys()
        clean_params = {k: v for k, v in params.items() if k in allowed_params}

        model = XGBRegressor(**clean_params)
        model.fit(X_train, y_train)

        preds = model.predict(X_test)
        rmse = np.sqrt(mean_squared_error(y_test, preds))
        r2 = r2_score(y_test, preds)

        logger.info(f"Modelo '{model_name}' entrenado. RMSE={rmse:.2f}, R2={r2:.2f}")
        return model, rmse, r2
    except Exception as e:
        logger.exception(f"Error al entrenar el modelo '{model_name}'.")
        raise e

# -------------------------------------------------------------------
# 5. Loggear en MLflow (solo si R2 > 0.83)
# -------------------------------------------------------------------
def log_with_mlflow(model, rmse, r2, model_name, register=False, registry_name="modelo_random"):
    try:
        if r2 <= 0.83:
            logger.warning(f"⚠️ Modelo con R²={r2:.4f} no cumple el umbral (0.83). No se guardará ni registrará.")
            return

        mlflow.set_tracking_uri("http://localhost:5000")
        mlflow.set_experiment("xgboost_models")

        with mlflow.start_run(run_name=model_name):
            for k, v in model.get_params().items():
                mlflow.log_param(k, v)
            mlflow.log_metric("rmse", rmse)
            mlflow.log_metric("r2", r2)

            timestamp = datetime.now().strftime("%Y%m%d_%H%M")
            model_dir = "Pipeline/models"
            os.makedirs(model_dir, exist_ok=True)
            model_path = os.path.join(model_dir, f"{model_name}_{timestamp}.pkl")

            # Guardar modelo local
            with open(model_path, "wb") as f:
                pickle.dump(model, f)

            logger.info(f"✅ Modelo guardado localmente en: {model_path}")
            mlflow.log_artifact(model_path)

            if register:
                mlflow.sklearn.log_model(model, name="model", registered_model_name=registry_name)
                logger.info(f"✅ Modelo registrado en MLflow como '{registry_name}'")
            else:
                mlflow.sklearn.log_model(model, name="model")
                logger.info(f"Modelo loggeado en MLflow sin registro formal.")

    except Exception as e:
        logger.exception(f"Error al loggear el modelo '{model_name}' en MLflow.")
        raise e

# -------------------------------------------------------------------
# MAIN SCRIPT
# -------------------------------------------------------------------
if __name__ == "__main__":
    try:
        logger.info("=== INICIO DEL ENTRENAMIENTO ===")

        data = load_clean_data()

        # Generar un set aleatorio de hiperparámetros
        params_random = get_random_params()
        logger.info(f"Hiperparámetros seleccionados aleatoriamente: {params_random}")

        X, y = prepare_features(data)

        # Entrenar modelo con parámetros aleatorios
        model_random, rmse_random, r2_random = train_new_model(X, y, params_random, model_name="xgboost_model_random")

        # Registrar y guardar el modelo solo si supera el umbral
        log_with_mlflow(model_random, rmse_random, r2_random, model_name="xgboost_model_random", register=True, registry_name="modelo_random")

        logger.info("=== FIN DEL ENTRENAMIENTO ===")

    except Exception as e:
        logger.exception("Error crítico en la ejecución principal del script.")
        raise e
