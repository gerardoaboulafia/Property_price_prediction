import mlflow
import mlflow.sklearn
import pandas as pd
import pickle
from xgboost import XGBRegressor
from sklearn.metrics import mean_squared_error, r2_score
import numpy as np
from preprocess.db_utils import get_connection, download_from_mysql
from sklearn.model_selection import train_test_split

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

    # Quedarme con las filas con flag = 'None'
    df = df[df["flag"] == "None"].copy()

    # Filtrar filas con NaN en la columna target
    df = df.dropna(subset=[target]).copy()

    # Asegurar que el target sea numérico
    df[target] = pd.to_numeric(df[target], errors="coerce")

    # Eliminar filas con inf en target
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
    
    # Ver shape final
    print(f"Shape de X: {X.shape}, Shape de y: {y.shape}")

    return X, y


# 4. Entrenar modelo con los hiperparámetros del pkl
def train_new_model(X, y, params, model_name="xgboost_model"):
    # Dividir los datos en train/test
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.3, random_state=42)

    # Filtrar solo los parámetros relevantes que XGBRegressor acepta
    allowed_params = XGBRegressor().get_params().keys()
    clean_params = {k: v for k, v in params.items() if k in allowed_params}

    model = XGBRegressor(**clean_params)
    model.fit(X_train, y_train)

    preds = model.predict(X_test)
    rmse = np.sqrt(mean_squared_error(y_test, preds))
    r2 = r2_score(y_test, preds)

    # Loggear en MLflow con un nombre de run dinámico
    log_with_mlflow(model, rmse, r2, model_name)
    
    return model, rmse, r2

# 5. Loggear en MLflow
def log_with_mlflow(model, rmse, r2, model_name):
    mlflow.set_tracking_uri("http://localhost:5000")
    mlflow.set_experiment("xgboost_models")  # Usamos el mismo experimento

    with mlflow.start_run(run_name=model_name):  # Nombre del run cambiado
        # Log de parámetros principales (si están en el modelo)
        for k, v in model.get_params().items():
            mlflow.log_param(k, v)

        # Log de métricas
        mlflow.log_metric("rmse", rmse)
        mlflow.log_metric("r2", r2)

        # Guardar el modelo como artefacto
        mlflow.sklearn.log_model(model, artifact_path="model")

        print(f"Modelo loggeado en MLflow con nombre '{model_name}' con RMSE={rmse:.2f} y R2={r2:.2f}")

if __name__ == "__main__":
    data = load_clean_data()
    params_0 = get_params_from_pkl()
    params_1 = {
    'objective': 'reg:squarederror',
    'eval_metric': 'rmse',
    'learning_rate': 0.1,
    'max_depth': 3,  # Menor profundidad
    'n_estimators': 2000,  # Más estimadores
    'subsample': 0.8,  # Submuestreo para evitar sobreajuste
    'colsample_bytree': 0.8,  # Muestra una fracción de las columnas
    'random_state': 5,
    'tree_method': 'hist',
    'enable_categorical': True
    }
    params_2 = {
    'objective': 'reg:squarederror',
    'eval_metric': 'rmse',
    'learning_rate': 0.05,  # Menor tasa de aprendizaje
    'max_depth': 6,  # Mayor profundidad
    'n_estimators': 500,  # Menos estimadores
    'subsample': 0.9,  # Aumento del tamaño de la muestra
    'colsample_bytree': 0.9,  # Aumento de la fracción de columnas
    'random_state': 5,
    'tree_method': 'hist',
    'enable_categorical': True
    }
    params_3 = {
    'objective': 'reg:squarederror',
    'eval_metric': 'rmse',
    'learning_rate': 0.1,
    'max_depth': 4,  # Profundidad intermedia
    'n_estimators': 1000,  # Estimadores intermedios
    'subsample': 0.7,  # Submuestreo
    'colsample_bytree': 0.7,  # Muestra menos columnas
    'reg_alpha': 0.1,  # Regularización L1
    'reg_lambda': 0.1,  # Regularización L2
    'random_state': 5,
    'tree_method': 'hist',
    'enable_categorical': True
    }
    X, y = prepare_features(data)
    # Entrenar varios modelos con diferentes hiperparámetros
    model_0, rmse_0, r2_0 = train_new_model(X, y, params_0, model_name="xgboost_retrained_with_pkl_params")
    model_1, rmse_1, r2_1 = train_new_model(X, y, params_1, model_name="xgboost_model_1")
    model_2, rmse_2, r2_2 = train_new_model(X, y, params_2, model_name="xgboost_model_2")
    model_3, rmse_3, r2_3 = train_new_model(X, y, params_3, model_name="xgboost_model_3")
    # Subir los modelos a MLflow
    log_with_mlflow(model_0, rmse_0, r2_0)
    log_with_mlflow(model_1, rmse_1, r2_1)
    log_with_mlflow(model_2, rmse_2, r2_2)
    log_with_mlflow(model_3, rmse_3, r2_3)