import sys, os
import numpy as np
import joblib

# Agregar el path raíz
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Ruta del modelo
model_path = os.path.join("Pipeline", "models", "model_api_test.pkl")
model = joblib.load(model_path)

def test_model_prediction_shape():
    """Verifica que el modelo cargue y produzca una predicción con la forma correcta."""
    
    # Detectar automáticamente el número de features
    n_features = getattr(model, "n_features_in_", 6)  # Usa 6 si no existe el atributo
    
    # Generar un vector aleatorio de entrada del tamaño correcto
    X = np.random.rand(1, n_features)
    
    # Obtener predicción
    y_pred = model.predict(X)
    
    # Validar la forma de salida
    assert y_pred.shape == (1,), f"La forma esperada es (1,), pero fue {y_pred.shape}"
