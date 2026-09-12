import google.generativeai as genai
from PIL import Image
import streamlit as st

# Configuración de página
st.set_page_config(
    page_title="AI Photo Prompt & LUT Generator", page_icon="📸", layout="centered"
)

st.title("📸 Arquitectura & Urbanismo AI Editor")
st.write(
    "Sube tu foto para analizar su histograma, perspectiva y color con IA gratuita."
)

# Barra lateral para configuración
with st.sidebar:
    st.header("Configuración")
    api_key = st.text_input(
        "Introduce tu Gemini API Key (Gratis):",
        type="password",
        help="Obtén tu clave gratis en https://aistudio.google.com/app/apikey",
    )

    estilo = st.radio(
        "Selecciona el Estilo de Acabado:",
        ["Normal (Editorial Equilibrado)", "High (Bold / Comercial)", "Soft (Fine Art / Mate)"],
        index=0,
    )

    st.markdown("---")
    st.caption("Motor de visión adaptativo con auto-detección de modelo.")

# Selector de archivo
uploaded_file = st.file_uploader(
    "Carga tu fotografía (JPG o PNG)", type=["jpg", "jpeg", "png"]
)

if uploaded_file is not None:
    image = Image.open(uploaded_file)
    st.image(image, caption="Fotografía cargada", use_container_width=True)

    if st.button("🚀 Analizar Foto y Generar Prompt", type="primary"):
        if not api_key:
            st.error(
                "Por favor, introduce tu Gemini API Key en la barra lateral para continuar."
            )
        else:
            with st.spinner("Conectando con la IA y analizando imagen..."):
                try:
                    # Configurar la API
                    genai.configure(api_key=api_key.strip())

                    # Buscar el mejor modelo disponible en la cuenta del usuario
                    modelos_disponibles = [
                        m.name
                        for m in genai.list_models()
                        if "generateContent" in m.supported_generation_methods
                    ]

                    # Prioridad de modelos de visión más rápidos y modernos
                    modelo_elegido = None
                    preferencias = [
                        "gemini-2.0-flash",
                        "gemini-1.5-flash-latest",
                        "gemini-1.5-flash",
                        "gemini-1.5-pro",
                        "gemini-pro-vision",
                    ]

                    for pref in preferencias:
                        for disp in modelos_disponibles:
                            if pref in disp:
                                modelo_elegido = disp
                                break
                        if modelo_elegido:
                            break

                    # Si no coincide ninguno de la lista, toma el primero que permita contenido
                    if not modelo_elegido and modelos_disponibles:
                        modelo_elegido = modelos_disponibles[0]

                    if not modelo_elegido:
                        st.error(
                            "No se encontraron modelos disponibles para esta clave de API."
                        )
                        st.stop()

                    # Instanciar el modelo detectado
                    model = genai.GenerativeModel(modelo_elegido)

                    prompt = f"""
Eres un Master Retoucher y Colorista Editorial de Arquitectura y Urbanismo de nivel mundial (referencia: Architectural Digest, El Croquis, National Geographic).

Tu misión es analizar la imagen subida en 4 ejes:
1. Rango dinámico y exposición.
2. Balance de blancos y dominantes cromáticas.
3. Distorsión de lente y convergencia de líneas de fuga (keystoning).
4. Micro-texturas y nitidez.

El usuario ha elegido el estilo de salida: **{estilo}**.

Genera una respuesta en Markdown con esta estructura exacta:

### 1. Diagnóstico Técnico de la Foto
(Explica brevemente qué problemas y virtudes tiene la imagen: ¿está subexpuesta? ¿hay dominantes cálidas/frías? ¿líneas torcidas? ¿pérdida de detalle en sombras?).

### 2. Prompt Maestro Adaptado
(Redacta el prompt maestro listo para usar en IA generativa o editores IA, incorporando las instrucciones específicas que necesita ESTA foto concreta y aplicando la variante de estilo elegida).

### 3. Receta Personalizada para Lightroom Mobile
(Proporciona los valores numéricos precisos (-100 a +100) que el usuario debe mover en su teléfono para esta imagen, cubriendo: Luz, Color, Efectos, Detalle y Geometría).
"""

                    response = model.generate_content([prompt, image])

                    st.success(
                        f"¡Análisis completado exitosamente con {modelo_elegido}!"
                    )
                    st.markdown("---")
                    st.markdown(response.text)

                except Exception as e:
                    st.error(f"Ocurrió un error al procesar la imagen: {e}")
