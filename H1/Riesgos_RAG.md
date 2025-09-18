# Evaluación de Riesgos (RAG) y Mitigaciones

A continuación se presentan los riesgos identificados en el trabajo práctico, junto con su nivel (RAG) y la estrategia de mitigación propuesta.

El primero es el riesgo de calidad de datos, asociado a la presencia de outliers, inconsistencias en las superficies declaradas y valores faltantes. Se lo clasifica como Rojo ya que impacta directamente en la confiabilidad de las predicciones. Para mitigarlo, se propusieron reglas de negocio como descartar superficies irreales, la imputación de valores faltantes y la detección de outliers teniendo en cuenta que características como superficie, precio y cantidad de ambientes se encuentren dentro de un rango razonable. 
**Métrica:** Proporción de datos erróneos que encontramos en los nuevos datos.
**Fecha tentativa:** 2/10/2025

El segundo riesgo es el de código difícil de mantener, que se ubica en nivel Amarillo. Este riesgo surge si no se estructura adecuadamente el código, lo que dificulta su comprensión y evolución. Como mitigación, se recomienda definir clases y métodos reutilizables, encapsular el pipeline en objetos y aplicar principios de programación orientada a objetos (OOP).
**Métrica:** Cantidad de clases que se usan en el proyecto y el tiempo que tarda en compilar (optimización)
**Fecha tentativa:** 13/11/2025


Por último, se considera el Model/Data Drift, es decir, los cambios en la distribución de los datos a lo largo del tiempo que pueden afectar la validez del modelo. Este riesgo se clasifica como Verde, dado que su impacto inmediato es bajo. No obstante, la mitigación propuesta incluye el monitoreo periódico del desempeño del modelo, la realización de retraining con datos nuevos y la implementación de tests unitarios para validar el comportamiento del sistema.
**Métrica:** Determinado porcentaje de predicciones fuera del rango esperado
**Fecha tentativa:** 16/10/2025


# Evaluación de Riesgos (RAG)

| Riesgo | Nivel (RAG) | Mitigación | Métrica | Fecha tentativa |
|--------|-------------|------------|---------|-----------------|
| **Calidad de datos** <br> (outliers, superficies irreales, valores faltantes) | 🔴 **Rojo** | - Reglas de negocio para descartar valores irreales <br> - Imputación de valores faltantes <br> - Detección de outliers (superficie, precio, ambientes en rango razonable) | % de datos erróneos detectados en nuevos datos | 02/10/2025 |
| **Código difícil de mantener** <br> (falta de estructura, baja reutilización) | 🟡 **Amarillo** | - Definir clases y métodos reutilizables <br> - Encapsular el pipeline en objetos <br> - Aplicar principios OOP | Nº de clases usadas + tiempo de compilación | 13/11/2025 |
| **Model/Data Drift** <br> (cambio en la distribución de datos con el tiempo) | 🟢 **Verde** | - Monitoreo periódico del desempeño <br> - Retraining con datos nuevos <br> - Tests unitarios para validar comportamiento | % de predicciones fuera del rango esperado | 16/10/2025 |
