import gradio as gr
import requests
import json
from datetime import datetime

# URL de tu API (ajusta si es necesario)
API_URL = "http://localhost:8000"

def predict_price(
    ciudad,
    barrio,
    sub_barrio,
    ambientes,
    dormitorios,
    banios,
    superficie_total,
    superficie_cubierta,
    tipo_propiedad,
    tipo_operacion,
    titulo,
    descripcion,
    latitud,
    longitud,
    precio
):
    """
    Envía los datos a la API y retorna la predicción
    """
    try:
        # Construir el payload con los nombres en español (alias)
        payload = {
            "Identificador": 1,
            "Tipo_de_Anuncio": "property",
            "Fecha_de_Inicio": datetime.now().strftime("%Y-%m-%d"),
            "Fecha_de_Fin": "2024-12-31",
            "Fecha_de_Creacion": datetime.now().strftime("%Y-%m-%d"),
            "Latitud": latitud if latitud else None,
            "Longitud": longitud if longitud else None,
            "Ciudad": ciudad,
            "Barrio": barrio,
            "Sub_barrio": sub_barrio,
            "Nivel_de_Ubicacion_4": None,
            "Nivel_de_Ubicacion_5": None,
            "Nivel_de_Ubicacion_6": None,
            "Ambientes": ambientes if ambientes else None,
            "Dormitorios": dormitorios if dormitorios else None,
            "Banios": banios if banios else None,
            "Superficie_Total_m2": superficie_total if superficie_total else None,
            "Superficie_Cubierta_m2": superficie_cubierta if superficie_cubierta else None,
            "Moneda": "USD",
            "Periodo_de_Precio": "monthly",
            "Titulo_del_Anuncio": titulo,
            "Descripcion_del_Anuncio": descripcion,
            "Tipo_de_Propiedad": tipo_propiedad,
            "Tipo_de_Operacion": tipo_operacion,
            "Precio": precio
        }
        
        # Hacer la petición POST a la API
        response = requests.post(
            f"{API_URL}/predict",
            json=payload,
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code == 200:
            result = response.json()
            
            if result["is_valid_for_prediction"]:
                precio_predicho = result["predicted_price"]
                features = result["input_features"]
                
                output = f"""
**PREDICCIÓN EXITOSA**

**Precio Predicho:** USD ${precio_predicho:,.2f}

**Características utilizadas:**
- Ambientes finales: {features.get('rooms_final', 'N/A')}
- M² finales: {features.get('m2_final', 'N/A')}
- Distancia al subte más cercano: {features.get('distancia_subte_cercano', 'N/A')} metros
- Barrio: {features.get('l2', 'N/A')}
- Tipo de propiedad: {features.get('property_type', 'N/A')}
"""
                return output
            else:
                return f"""
**DATOS NO VÁLIDOS**

Los datos no pasaron la validación del preprocesamiento.
Flags: {result.get('preprocessing_flags', 'N/A')}

Por favor, verifica los datos ingresados.
"""
        else:
            error_detail = response.json().get("detail", "Error desconocido")
            return f" **ERROR:** {error_detail}"
            
    except requests.exceptions.ConnectionError:
        return " **ERROR DE CONEXIÓN:** No se pudo conectar a la API. Asegúrate de que esté corriendo en http://localhost:8000"
    except Exception as e:
        return f" **ERROR INESPERADO:** {str(e)}"

# Crear la interfaz de Gradio
with gr.Blocks(title="Predicción de Precios de Propiedades", theme=gr.themes.Soft()) as demo:
    gr.Markdown(
        """
        # Predicción de Precios de Propiedades
        ### Completa los datos de la propiedad para obtener una predicción de precio
        """
    )
    
    with gr.Row():
        with gr.Column():
            gr.Markdown("### Ubicación")
            ciudad = gr.Textbox(label="Ciudad", value="Argentina", placeholder="Argentina")
            barrio = gr.Textbox(label="Barrio", value="Capital Federal", placeholder="Capital Federal")
            sub_barrio = gr.Textbox(label="Sub-barrio", placeholder="Ej: Palermo, Recoleta, Belgrano")
            
            with gr.Row():
                latitud = gr.Number(label="Latitud", value=-34.5900, precision=4)
                longitud = gr.Number(label="Longitud", value=-58.4200, precision=4)
        
        with gr.Column():
            gr.Markdown("### Características de la Propiedad")
            tipo_propiedad = gr.Dropdown(
                label="Tipo de Propiedad",
                choices=["Departamento", "Casa", "PH", "Local", "Oficina"],
                value="Departamento"
            )
            tipo_operacion = gr.Dropdown(
                label="Tipo de Operación",
                choices=["Venta", "Alquiler"],
                value="Venta"
            )
            
            with gr.Row():
                ambientes = gr.Number(label="Ambientes", value=2, precision=0)
                dormitorios = gr.Number(label="Dormitorios", value=1, precision=0)
                banios = gr.Number(label="Baños", value=1, precision=0)
            
            with gr.Row():
                superficie_total = gr.Number(label="Superficie Total (m²)", value=65, precision=1)
                superficie_cubierta = gr.Number(label="Superficie Cubierta (m²)", value=60, precision=1)
    
    with gr.Row():
        with gr.Column():
            gr.Markdown("### Información del Anuncio")
            titulo = gr.Textbox(
                label="Título del Anuncio",
                value="Departamento 2 ambientes 65m2 Palermo",
                placeholder="Título descriptivo de la propiedad"
            )
            descripcion = gr.TextArea(
                label="Descripción",
                value="Hermoso departamento de 2 ambientes en Palermo, 65 metros cuadrados",
                placeholder="Descripción detallada de la propiedad",
                lines=3
            )
            precio = gr.Number(
                label="Precio Publicado (USD)",
                value=185000,
                info="Este precio se usa para el preprocesamiento, no afecta la predicción"
            )
    
    predict_btn = gr.Button(" Predecir Precio", variant="primary", size="lg")
    
    gr.Markdown("### Resultado de la Predicción")
    output = gr.Markdown()
    
    predict_btn.click(
        fn=predict_price,
        inputs=[
            ciudad, barrio, sub_barrio, ambientes, dormitorios, banios,
            superficie_total, superficie_cubierta, tipo_propiedad, tipo_operacion,
            titulo, descripcion, latitud, longitud, precio
        ],
        outputs=output
    )
    
    gr.Markdown(
        """
        ---
        **Nota:** Asegúrate de que la API esté corriendo en `http://localhost:8000` antes de usar esta interfaz.
        
        Para iniciar la API: `python -m uvicorn app.main:app --reload`
        """
    )

if __name__ == "__main__":
    demo.launch(
        server_name="0.0.0.0",
        server_port=7860,
        share=False
    )
