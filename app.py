import os
import time
import streamlit as st
import google.generativeai as genai

# Configuración de la página, título y favicon oficial de Cuarto Espacio
st.set_page_config(
    page_title="Cuarto Espacio | Simulador de Oratoria",
    page_icon="https://cuartoespacio.co/wp-content/uploads/2021/04/cropped-favicon-1-32x32.png",
    layout="wide"
)

# Estilos CSS avanzados para la estética limpia y moderna
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
    
    .stApp {
        background-color: #030712;
        color: #f3f4f6;
        font-family: 'Inter', sans-serif;
    }
    
    /* Eliminar padding superior predeterminado de Streamlit */
    .block-container {
        padding-top: 1.5rem !important;
        max-width: 55rem !important;
    }
    
    /* Ocultar elementos predeterminados */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    
    /* Estilos de tipografía y títulos */
    h1, h2, h3 {
        color: #f9fafb !important;
        font-family: 'Inter', sans-serif;
        font-weight: 700;
    }
    
    /* Botones personalizados con gradiente morado de marca */
    .stButton>button {
        background: linear-gradient(to right, #7c3aed, #8b5cf6) !important;
        color: white !important;
        border: none !important;
        border-radius: 0.75rem !important;
        font-weight: 600 !important;
        padding: 0.6rem 1.2rem !important;
        box-shadow: 0 10px 15px -3px rgba(124, 58, 237, 0.3) !important;
        transition: all 0.3s ease !important;
        width: 100%;
    }
    
    .stButton>button:hover {
        opacity: 0.9 !important;
        box-shadow: 0 15px 20px -3px rgba(124, 58, 237, 0.4) !important;
    }
    
    /* Estilo para los File Uploaders */
    div[data-testid="stFileUploader"] {
        background-color: #111827;
        border: 2px dashed #374151;
        border-radius: 1rem;
        padding: 1rem;
        text-align: center;
    }
    div[data-testid="stFileUploader"]:hover {
        border-color: #8b5cf6;
    }
    
    /* RESTRINGIR EL TAMAÑO DEL PREVIEW DEL VIDEO */
    div[data-testid="stVideo"] {
        max-width: 400px;
        margin: 0 auto;
        border-radius: 1rem;
        overflow: hidden;
    }
    div[data-testid="stVideo"] video {
        max-height: 300px;
        object-fit: contain;
    }
</style>
""", unsafe_allow_html=True)

# Configuración de la API Key de Gemini
API_KEY = "AIzaSyDLETiXyT5p3hrxzPBFo_UUNaIIpVUPb4U"
genai.configure(api_key=API_KEY)

# Título y Subtítulo
st.markdown("""
<div style="text-align: center; max-width: 48rem; margin: 0 auto 1.5rem auto;">
    <h2 style="font-size: 2rem; font-weight: 800; letter-spacing: -0.025em; margin-bottom: 0.5rem;">Evalúa tu oratoria con precisión de experto</h2>
    <p style="color: #9ca3af; font-size: 0.95rem;">Sube un archivo, grábate directamente o ingresa un enlace de YouTube para recibir un análisis multimodal profundo.</p>
</div>
""", unsafe_allow_html=True)

# Pestañas de Selección de Entrada
tab_upload, tab_record, tab_youtube = st.tabs(["📁 Subir Archivo", "🎥 Grabar Video", "▶️ Enlace de YouTube"])

video_to_process = None

with tab_upload:
    uploaded_file = st.file_uploader("Sube tu archivo de video (.mp4, .mov, .webm)", type=["mp4", "mov", "webm"])
    if uploaded_file is not None:
        video_to_process = uploaded_file

with tab_record:
    st.markdown("### Graba tu intervención directamente:")
    recorded_file = st.camera_input("Usa tu cámara para grabar un discurso corto")
    if recorded_file is not None:
        video_to_process = recorded_file

with tab_youtube:
    st.markdown("### Análisis de Discursos de YouTube:")
    youtube_url = st.text_input("Pega el enlace del video de YouTube (ej. TED Talk, presentación):")
    if youtube_url:
        st.info("ℹ️ Nota: Para videos de YouTube directamente con enlace, asegúrate de utilizar un archivo descargado o usa las opciones de subida si el servidor requiere procesamiento multimodal nativo de archivos directos.")

# Si hay un archivo de video listo para procesar (subido o grabado)
if video_to_process is not None:
    st.video(video_to_process)
    
    if st.button("⚡ Iniciar Análisis con IA"):
        with st.spinner("⏳ Subiendo video y analizando a profundidad con Gemini..."):
            gemini_file = None
            try:
                temp_path = os.path.join("/tmp", getattr(video_to_process, "name", "video_grabado.mp4"))
                with open(temp_path, "wb") as f:
                    f.write(video_to_process.getbuffer())

                gemini_file = genai.upload_file(temp_path)
                
                while gemini_file.state.name == "PROCESSING":
                    time.sleep(2)
                    gemini_file = genai.get_file(gemini_file.name)
                    
                if gemini_file.state.name != "ACTIVE":
                    raise Exception("El archivo no pudo ser procesado.")

                model = genai.GenerativeModel('gemini-2.5-flash')
                
                prompt = """
                Actúa como un estricto, riguroso y experto coach de oratoria ejecutiva de Cuarto Espacio. 
                Realiza un análisis multimodal exhaustivo y profesional de este video. Tu evaluación debe estar estructurada exactamente con los siguientes apartados:

                1. 📊 **Nivel de Convicción Global y Calificación General:**
                   - Da una valoración directa sobre qué tan convincente y persuasivo es el orador en general.
                   - Nivel de impacto percibido (escala de 1 a 10).

                2. 🦾 **Lenguaje Corporal, Gestos y Postura:**
                   - Evaluación de la apertura de hombros, postura corporal y firmeza ejecutiva.
                   - Análisis de la expresividad facial y los gestos de las manos (¿aportan dinamismo o son distractores?).

                3. 🎵 **Voz, Entonación y Contrastes Vocales:**
                   - Modulación, ritmo, volumen y proyección vocal.
                   - Uso de contrastes vocales (velocidad, énfasis, silencios y pausas estratégicas).

                4. 🎯 **Estructura del Pitch, Discurso y Nivel de Persuasión:**
                   - ¿Cómo arranca el gancho inicial? ¿Atrapa la atención?
                   - Estructura lógica del mensaje y fuerza del llamado a la acción (CTA) o cierre.

                5. 💡 **Recomendaciones Prácticas de Mejora Inmediata:**
                   - Acciones concretas y tácticas que el orador debe aplicar de inmediato para elevar su nivel de impacto.
                """
                
                response = model.generate_content([gemini_file, prompt])
                
                st.markdown("### 📊 Reporte Completo del Coach de Oratoria")
                st.markdown(response.text)
                
            except Exception as e:
                st.error(f"❌ Error de procesamiento: {str(e)}")
                
            finally:
                if gemini_file:
                    try:
                        genai.delete_file(gemini_file.name)
                    except:
                        pass
