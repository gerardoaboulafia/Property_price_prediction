# One Pager


## Problema que se resuelve
Se realizó un trabajo enfocado en la predicción del precio de propiedades, específicamente de departamentos, casas y PHs ubicados en la Ciudad Autónoma de Buenos Aires, con valores expresados en dólares estadounidenses (USD). El objetivo principal es desarrollar un modelo que permita estimar el valor de venta de manera más confiable y precisa que un modelo base, en este caso una Regresión Lineal.

## Datos utilizados
El dataset contiene características descritivas de las propiedades, entre las más relevantes se incluyen: superficie cubierta, superficie total, cantidad de ambientes, tipo de propiedad, ubicación geográfica (por barrio) y precio expresado en dólares estadounidenses, además de otras variables complementarias.

Este conjunto de datos proviene de la plataforma Properati, reconocida fuente de información del mercado inmobiliario en Argentina.

Con el objetivo de preparar la información para el modelado predictivo, se realizó un proceso de análisis y depuración. En primer lugar, se aplicó un estudio de estadística descriptiva, lo cual permitió comprender la distribución de las variables, identificar valores atípicos y detectar posibles inconsistencias en los registros. Posteriormente, se llevó a cabo una fase de limpieza de datos, que incluyó la imputación de valores nulos y la verificación de filtros para garantizar que los registros utilizados fueran consistentes y representativos de la realidad del mercado.

Adicionalmente, se implementaron técnicas de normalización y transformación de variables, con el fin de homogeneizar escalas y optimizar el rendimiento del modelo. Finalmente, se realizó una selección de variables, identificando aquellas características con mayor poder explicativo sobre el precio de las propiedades y descartando información redundante o poco significativa.

## Modelo aplicado
Para la etapa de modelado se seleccionó el algoritmo XGBoost Regressor (Extreme Gradient Boosting), un método de boosting basado en árboles de decisión que se destaca por su alto rendimiento en tareas de regresión y clasificación. La elección de este modelo se fundamenta en su capacidad para capturar relaciones no lineales entre las variables, su robustez frente a datos heterogéneos y su buen balance entre sesgo y varianza.

Previo al entrenamiento, se dividió el conjunto de datos en subconjuntos de entrenamiento y prueba, y posteriormente se realizó un ajuste de hiperparámetros con el objetivo de mejorar la precisión de las predicciones y evitar el sobreajuste.

El modelo fue evaluado mediante métricas de error como MAE (Mean Absolute Error), RMSE (Root Mean Squared Error) y MAPE (Mean Absolute Percentage Error), las cuales permiten cuantificar la diferencia entre los precios reales y los predichos.


## Planificación
Con el modelo actual se logró una primera aproximación robusta para la predicción de precios de propiedades en la Ciudad de Buenos Aires. Sin embargo, se identificaron varias líneas de trabajo futuras que permitirán escalar, automatizar y mejorar el sistema:

- Rediseño del pipeline con Programación Orientada a Objetos (POO): se busca estructurar el flujo de preprocesamiento y modelado de manera más modular y reutilizable, facilitando la mantenibilidad del código y la incorporación de nuevas funcionalidades.

- Implementación de herramientas de monitoreo: se explorarán soluciones para supervisar el desempeño del modelo en producción, permitiendo detectar caídas en la precisión, identificar sesgos y asegurar la estabilidad de las predicciones en el tiempo.

- Despliegue mediante API y contenedores: el modelo será expuesto a través de una API REST, que permitirá enviar información de una propiedad y recibir como respuesta la predicción de su precio. Para garantizar portabilidad y escalabilidad, se prevé la dockerización del modelo, lo que facilitará su ejecución en distintos entornos de manera eficiente.

- Evaluación de data drift: se establecerán procesos para analizar periódicamente si la distribución de los datos en producción se desvía respecto del dataset original de entrenamiento. Esto permitirá identificar cuándo es necesario reentrenar el modelo para mantener la calidad de las predicciones.