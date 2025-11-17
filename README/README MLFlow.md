# Guía de pasos para registrar un modelo en MLFlow y correr la API

## MLFlow
### Requisitos
-Tener instalado MySQL Workbench y MySQL Shell en la computadora

-Librerías:
pip install mlflow pandas xgboost scikit-learn numpy

### Pasos
1- Ejecutar el archivo inicializacion_mlflow (Pipeline\inicializacion_mlflow.py).

2- Una vez inicializado mlflow, dirigirse al archivo registro_exp_ml_flow (Pipeline\registro_exp_mlflow.py).
   Allí se encuentra detallado ya el usuario y la contraseña de MySQL, si ya está instalado correctamente debería correr sin problemas, por lo que no es necesario modificar los mismos para que funcione. En la consola debe aparecer el mensaje 
   
   INFO:     Application startup complete.

   una vez que inicializó correctamente.

3- Para entrenar y testear un modelo (presisamente un XGBoost) se debe llamar a la función train_new_model, la cual se le deben pasar como parámetros X, las categorías a tener en cuenta; y, la variable target; params, que representa un diccionario con los parámetros del modelo, y model_name, que si no se le pasa nada automáticamente lo denomina "xgboost_model".
   Los parámetros deben guardarse como en el siguiente ejemplo:

```python
params_ej = {
    'objective': 'reg:squarederror',
    'eval_metric': 'rmse',
    'learning_rate': 0.1,
    'max_depth': 3,
    'n_estimators': 2000,
    'subsample': 0.8,
    'colsample_bytree': 0.8,
    'random_state': 5,
    'tree_method': 'hist',
    'enable_categorical': True
}
```

También es posible generar un conjunto aleatorio de hiperparámetros utilizando la función:

```python
params_random = get_params()

```

4- Al llamar a la función train_new_model, se debe guardar en variables, además del modelo, las métricas del mismo, presisamente el RMSE y R2. Se guarda en el mismo orden presentado, a continuación se detalla un ejemplo de como debe correrse y almacenar correctamente la función y sus respectivos resultados:

   model_ej, rmse_ej, r2_ej = train_new_model(X, y, params_ej, model_name="xgboost_ej")

5- Una vez guardado el modelo, se debe subir el mismo a MLFlow llamando a la función log_ml_flow y pasándole los siguientes parámetros: model; rmse; r2; model_name, register, el cual se le debe pasar register=False, si no se quiere REGISTRAR el modelo (diferente a almacenar dentro de MLFlow en un experimento), caso contrario se le debe pasar register=True; y por último registry_name, que si no se le pasa nada automáticamete se lo resgistra como "modelo_api_p". Así se vería un ejemplo a la hora de llamar a la función:

   log_with_mlflow(model_2, rmse_2, r2_2, model_name="xgboost_ej", register=True, registry_name="modelo_ej")

   

6- Una vez registrado el/los modelo/s, se debe cerrar sesión en MLFlow. Para ello, se debe ir a la consola donde se corrió el archivo (debe tener como nombre "Python: inicializacion_mlflow") y apretar CTRL+C, una vez cerrada debe imprimirse el mensaje:

   INFO:     Shutting down
   INFO:     Waiting for application shutdown.
   INFO:     Application shutdown complete.
   INFO:     Finished server process [17756]
   
   el cual indica que se cerró MLFlow correctamente.

### Nota importante sobre el guardado de modelos

Los modelos solo se guardan si superan un umbral mínimo de desempeño, precisamente se debe tener un **R² mayor a 0.83**.

Si el modelo no supera ese umbral, **no se guarda en disco ni se sube a MLflow**.



