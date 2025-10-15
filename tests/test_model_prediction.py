import sys, os
import numpy as np
import joblib

# 🔧 Agregar el path raíz del proyecto para importar módulos
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# 🧠 Cargamos el modelo entrenado desde la carpeta models
# (ajustá el nombre si tu archivo del modelo tiene otro nombre)
model_path = os.path.join("Pipeline", "models", "model.joblib")
model = joblib.load(model_path)

def test_model_prediction_shape():
    """Verifica que el modelo devuelva una predicción de forma (1,)."""
    X = np.array([[2, 50, 1]])  # Ejemplo: 3 features
    y_pred = model.predict(X)
    assert y_pred.shape == (1,), f"La forma de salida esperada es (1,), pero fue {y_pred.shape}"
