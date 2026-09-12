import base64
import io
from openai import OpenAI
from PIL import Image
import streamlit as st

# Configuración de página
st.set_page_config(
    page_title="AI Photo Prompt & LUT Generator", page_icon="📸", layout="centered"
)

st.title("📸 Arquitectura & Urbanismo AI Editor")
st.write(
    "Sube tu foto para analizar su histograma, perspectiva y color con **GitHub Models (GPT-4o-mini)**."
)

# Barra lateral para configuración
with st.sidebar:
    st.header("Configuración")
    api_key = st.text_input(
        "Introduce tu GitHub Token (ghp_...):",
        type="password",
        help="Obtenlo gratis en https://github.com/settings/tokens/new",
    )

    estilo = st.radio(
        "Selecciona el Estilo de Acabado:",
        ["Normal (Editorial Equilibrado)", "High (Bold / Comercial)", "Soft (Fine Art / Mate)"],
        index=0,
    )

    st.markdown("---")
    st.caption("Impulsado por GitHub Models & Azure AI.")


# Función para redimensionar y codificar imagen
def procesar_imagen_base64(img_pil, max_dim=1200):
    img = img_pil.convert("RGB")
    img.thumbnail((max_dim, max_dim), Image.Resampling.LANCZOS)
    buffered = io.BytesIO()
    img.save(buffered, format="JPEG", quality=85)
    return base64.b64encode(buffered.getvalue()).decode("utf-8")


# Selector de archivo
uploaded_file = st.file_uploader(
    "Carga tu fotografía (JPG o PNG)", type=["jpg", "jpeg", "png"]
)

if uploaded_file is not None:
    raw_image = Image.open(uploaded_file)
    st.image(raw_image, caption="Fotografía cargada", use_container_width=True)

    if st.button("🚀 Analizar Foto y Generar Prompt", type="primary"):
        if not api_key:
            st.error(
                "Por favor, introduce tu GitHub Token (ghp_...) en la barra lateral."
            )
        else:
            with st.spinner("Procesando con GPT-4o-mini (GitHub Models)..."):
                try:
                    # Cliente OpenAI apuntando al Endpoint de GitHub Models
                    client = OpenAI(
                        base_url="https://models.inference.ai.azure.com",
                        api_key=api_key.strip(),
                    )

                    base64_image = procesar_imagen_base64(raw_image)

                    prompt_sistema = f"""
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

                    response = client.chat.completions.create(
                        model="gpt-4o-mini",
                        messages=[
                            {"role": "system", "content": prompt_sistema},
                            {
                                "role": "user",
                                "content": [
                                    {
                                        "type": "text",
                                        "text": "Analiza esta fotografía y genera el informe técnico y el prompt correspondiente.",
                                    },
                                    {
                                        "type": "image_url",
                                        "image_url": {
                                            "url": f"data:image/jpeg;base64,{base64_image}"
                                        },
                                    },
                                ],
                            },
                        ],
                        max_tokens=1500,
                    )

                    resultado = response.choices[0].message.content

                    st.success(
                        "¡Análisis completado exitosamente con GitHub Models!"
                    )
                    st.markdown("---")
                    st.markdown(resultado)

                except Exception as e:
                    st.error(f"Error técnico: {str(e)}")
