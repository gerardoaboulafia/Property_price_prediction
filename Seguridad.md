# Seguridad y Protección de Datos (PII)

Nuestra API de Predicción de Precios de Propiedades fue diseñada considerando las buenas prácticas de **seguridad y privacidad de datos**.  

### 1. No exposición de datos sensibles
- La API recibe como entrada datos potencialmente identificables (por ejemplo: coordenadas exactas `lat`, `lon`, títulos y descripciones textuales).  
- **Sin embargo, nunca devuelve esa información tal cual en la respuesta.**  
- En su lugar, la API responde únicamente con atributos **procesados o agregados**, tales como:
  - `place_l3`: barrio de la propiedad (nivel agregado, no dirección exacta).  
  - `type`: tipo de propiedad (ej. “Departamento”).  
  - `rooms_final`, `m2_final`: características generales.  
  - `distancia_subte_cercano`: dato derivado de cálculo, sin riesgo de identificar al propietario.  

De esta forma, garantizamos que **la ubicación exacta y los datos originales de la publicación no se expongan al usuario final**.  

### 2. Riesgos de PII en datasets inmobiliarios
Aunque nuestro dataset no incluye información personal sensible como DNI, emails o teléfonos, sí contiene atributos que pueden considerarse **PII indirecta**:
- Coordenadas geográficas exactas (pueden señalar un domicilio).  
- Textos de `title` o `description` que, en casos reales, podrían incluir direcciones.  

Por esta razón, la API fue diseñada para **usar estos datos internamente para el modelo, pero nunca exponerlos directamente en la respuesta**.  

### 3. Recomendaciones para producción
En un entorno productivo se deberían aplicar medidas adicionales:
- **Anonimizar coordenadas**: Redondear `lat/lon` a 3 decimales o transformarlas a nivel de manzana/barrio.  
- **Sanear textos**: Evitar devolver direcciones exactas o referencias personales en `title` o `description`.  
- **Protección en tránsito**: Asegurar que toda comunicación cliente-servidor ocurra mediante **HTTPS** para evitar fugas de datos en redes inseguras.  
- **Control de acceso**: Limitar el uso de la API mediante autenticación (ej. tokens o API keys) en caso de exposición pública.  
- **Logging seguro**: Si se registran requests/responses, anonimizar datos sensibles antes de guardarlos en logs.  

### 4. Compromiso de la API
Gracias a este diseño, nuestra API:
- **Cumple con el principio de mínima exposición** → solo devuelve lo necesario para la predicción.  
- **Separa claramente inputs y outputs** → lo sensible se usa internamente, lo agregado se devuelve al usuario.  
- **Está preparada para escalar** con medidas de seguridad adicionales en un entorno real.  

En conclusión, la API no solo entrega predicciones de precios, sino que también incorpora desde su diseño consideraciones de **privacidad y seguridad**, alineándose con buenas prácticas de manejo de PII en aplicaciones de datos.
