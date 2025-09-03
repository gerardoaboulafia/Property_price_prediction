# Sanity Check

Para asegurar la coherencia y calidad del dataset antes del modelado, se implementó un proceso de sanity check orientado a identificar registros inconsistentes o fuera de rango esperado.

En primer lugar, se establecieron umbrales razonables para las principales variables:

- El precio de las propiedades debía encontrarse entre 20.000 y 1.500.000 USD, de modo de excluir valores irreales o inconsistentes con el mercado de Capital Federal.

- El número de ambientes se acotó entre 1 y 15, descartando casos con una cantidad nula o excesiva de habitaciones.

- La superficie cubierta se restringió al rango de 20 a 500 m², evitando registros con valores atípicos extremos.

Los registros que no cumplieron estas condiciones fueron marcados automáticamente mediante la función flag_outliers, lo que permitió identificarlos y tratarlos de forma diferenciada.

Adicionalmente, se aplicaron estrategias para la imputación de valores faltantes en variables clave. Por ejemplo, cuando no se encontraba informada la cantidad de ambientes, los metros cuadrados o la distancia al subte más cercano, se completaron dichos valores utilizando el promedio correspondiente al barrio, asegurando consistencia con el contexto geográfico.

En los casos en que los datos de habitaciones o superficie cubierta estaban ausentes, se emplearon expresiones regulares sobre el título de la propiedad para extraer información y completar la variable faltante.

Por último, se verificó que todas las propiedades incluidas efectivamente pertenecieran a la Ciudad Autónoma de Buenos Aires. Para ello, se utilizó el multipolígono oficial de CABA como referencia espacial, contrastando la ubicación reportada de cada propiedad con los límites geográficos reales. Aquellos registros que figuraban dentro del dataset pero no se encontraban en los límites de CABA fueron descartados.

Para el control de calidad, se incorporó una columna de flag que permitió rastrear los registros detectados en cada paso de verificación. Finalmente, únicamente se conservaron aquellas observaciones que cumplían con todas las condiciones de consistencia, asegurando un dataset confiable para el entrenamiento del modelo predictivo.

Este proceso de verificación y limpieza garantizó que el conjunto de datos utilizado para entrenar el modelo estuviera libre de inconsistencias graves, mejorando la confiabilidad de las predicciones posteriores.

Esto se encuentra en Pipeline -> Preprocess -> Pycache -> Clean_data