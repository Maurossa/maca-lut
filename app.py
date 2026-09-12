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
        help="La clave copiada desde Google AI Studio.",
    )

    estilo = st.radio(
        "Selecciona el Estilo de Acabado:",
        ["Normal (Editorial Equilibrado)", "High (Bold / Comercial)", "Soft (Fine Art / Mate)"],
        index=0,
    )

    st.markdown("---")
    st.caption("Motor de visión adaptativo.")

# Selector de archivo
uploaded_file = st.file_uploader(
    "Carga tu fotografía (JPG o PNG)", type=["jpg", "jpeg", "png"]
)

if uploaded_file is not None:
    # Asegurar compatibilidad de formato de imagen (RGB)
    raw_image = Image.open(uploaded_file)
    image = raw_image.convert("RGB")
    st.image(image, caption="Fotografía cargada", use_container_width=True)

    if st.button("🚀 Analizar Foto y Generar Prompt", type="primary"):
        if not api_key:
            st.error(
                "Por favor, introduce tu Gemini API Key en la barra lateral para continuar."
            )
        else:
            with st.spinner("Consultando modelos y analizando imagen..."):
                try:
                    # Configurar la API
                    clean_key = api_key.strip()
                    genai.configure(api_key=clean_key)

                    # Listar modelos disponibles en la cuenta
                    modelos_disponibles = []
                    for m in genai.list_models():
                        if "generateContent" in m.supported_generation_methods:
                            modelos_disponibles.append(m.name)

                    if not modelos_disponibles:
                        st.error(
                            "Tu clave es válida, pero tu proyecto no tiene ningún modelo habilitado en Google Cloud."
                        )
                        st.stop()

                    # Seleccionar el mejor modelo de visión disponible
                    modelo_a_usar = None
                    preferencias = [
                        "gemini-1.5-flash",
                        "gemini-2.0-flash",
                        "gemini-1.5-flash-latest",
                        "gemini-1.5-pro",
                    ]

                    for pref in preferencias:
                        for disp in modelos_disponibles:
                            if pref in disp:
                                modelo_a_usar = disp
                                break
                        if modelo_a_usar:
                            break

                    if not modelo_a_usar:
                        modelo_a_usar = modelos_disponibles[0]

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

                    model = genai.GenerativeModel(modelo_a_usar)
                    response = model.generate_content([prompt, image])

                    st.success(
                        f"¡Análisis completado exitosamente con {modelo_a_usar}!"
                    )
                    st.markdown("---")
                    st.markdown(response.text)

                except Exception as e:
                    st.error(f"Detalle técnico del error: {str(e)}")
