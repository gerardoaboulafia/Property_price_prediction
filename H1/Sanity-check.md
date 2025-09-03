# Sanity Check

Para asegurar la coherencia y calidad del dataset antes del modelado, se implementó un proceso de sanity check orientado a identificar registros inconsistentes o fuera de rango esperado.

En primer lugar, se establecieron umbrales razonables para las principales variables:

- El precio de las propiedades debía encontrarse entre 20.000 y 1.500.000 USD, de modo de excluir valores irreales o inconsistentes con el mercado de Capital Federal.

- El número de ambientes se acotó entre 1 y 15, descartando casos con una cantidad nula o excesiva de habitaciones.

- La superficie cubierta se restringió al rango de 20 a 500 m², evitando registros con valores atípicos extremos.

Los registros que no cumplieron estas condiciones fueron marcados automáticamente mediante la función flag_outliers, lo que permitió identificarlos y tratarlos de forma diferenciada.

Además, se diseñó un procedimiento de imputación de valores faltantes en variables clave. Por ejemplo, en los casos en que la cantidad de ambientes, la superficie o la distancia al subte no estaban informadas, dichos valores fueron reemplazados por el promedio del barrio correspondiente, manteniendo la coherencia geográfica y reduciendo el sesgo de la imputación.

Este proceso de verificación y limpieza garantizó que el conjunto de datos utilizado para entrenar el modelo estuviera libre de inconsistencias graves, mejorando la confiabilidad de las predicciones posteriores.

Esto se encuentra en Pipeline -> Preprocess -> Pycache -> Clean_data