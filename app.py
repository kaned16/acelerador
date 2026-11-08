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

# Estilos CSS avanzados para maquetar el reproductor pequeño al lado del botón y las tarjetas de los 5 ítems
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
    
    .stApp {
        background-color: #030712;
        color: #f3f4f6;
        font-family: 'Inter', sans-serif;
    }
    
    /* Eliminar padding superior predeterminado */
    .block-container {
        padding-top: 1.5rem !important;
        max-width: 55rem !important;
    }
    
    /* Ocultar elementos predeterminados de Streamlit */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    
    /* Estilos de tipografía y títulos */
    h1, h2, h3 {
        color: #f9fafb !important;
        font-family: 'Inter', sans-serif;
        font-weight: 700;
    }
    
    /* Estilizar los botones de navegación superiores */
    div.stButton > button {
        background-color: #111827 !important;
        color: #9ca3af !important;
        border: 1px solid #1f2937 !important;
        border-radius: 0.75rem !important;
        font-weight: 600 !important;
        padding: 0.5rem 0.75rem !important;
        font-size: 0.85rem !important;
        box-shadow: none !important;
        transition: all 0.2s ease !important;
        width: 100%;
        white-space: nowrap;
    }
    
    div.stButton > button:hover {
        background-color: #1f2937 !important;
        color: #ffffff !important;
        border-color: #374151 !important;
    }

    /* Botón principal de análisis con gradiente */
    div.stButton.analizar-btn > button {
        background: linear-gradient(to right, #7c3aed, #8b5cf6) !important;
        color: white !important;
        border: none !important;
        padding: 0.75rem 1.5rem !important;
        font-size: 1rem !important;
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

    /* RESTRINGIR EL TAMAÑO DEL PREVIEW DEL VIDEO A UN CUADRITO PEQUEÑO */
    div[data-testid="stVideo"] {
        max-width: 240px;
        border-radius: 0.75rem;
        overflow: hidden;
        border: 1px solid #1f2937;
    }
    div[data-testid="stVideo"] video {
        max-height: 140px;
        object-fit: cover;
    }
</style>
""", unsafe_allow_html=True)

# Configuración segura de la API Key desde los Secrets de Streamlit Cloud
try:
    API_KEY = st.secrets["GEMINI_API_KEY"]
except Exception:
    API_KEY = "AIzaSyDLETiXyT5p3hrxzPBFo_UUNaIIpVUPb4U"

genai.configure(api_key=API_KEY)

# Título y Subtítulo
st.markdown("""
<div style="text-align: center; max-width: 48rem; margin: 0 auto 1.5rem auto;">
    <h2 style="font-size: 2.0rem; font-weight: 800; letter-spacing: -0.025em; margin-bottom: 0.5rem;">Evalúa tu oratoria con precisión de experto</h2>
    <p style="color: #9ca3af; font-size: 0.95rem;">Sube un archivo, grábate directamente o ingresa un enlace de YouTube para recibir un análisis multimodal profundo.</p>
</div>
""", unsafe_allow_html=True)

# Control de estado para las opciones de entrada
if "input_mode" not in st.session_state:
    st.session_state["input_mode"] = "upload"

# Renderizar los 3 botones en línea horizontal sin emojis
col1, col2, col3 = st.columns(3)

with col1:
    if st.button("Subir Archivo", key="btn_upload"):
        st.session_state["input_mode"] = "upload"
        st.rerun()

with col2:
    if st.button("Grabar Video", key="btn_record"):
        st.session_state["input_mode"] = "record"
        st.rerun()

with col3:
    if st.button("YouTube", key="btn_youtube"):
        st.session_state["input_mode"] = "youtube"
        st.rerun()

st.markdown("<div style='margin-bottom: 1rem;'></div>", unsafe_allow_html=True)

video_to_process = None

# Contenido según la opción seleccionada
if st.session_state["input_mode"] == "upload":
    uploaded_file = st.file_uploader("Sube tu archivo de video (.mp4, .mov, .webm)", type=["mp4", "mov", "webm"])
    if uploaded_file is not None:
        video_to_process = uploaded_file

elif st.session_state["input_mode"] == "record":
    st.markdown("<p style='text-align: center; color: #9ca3af; font-size: 0.9rem;'>Usa tu cámara para grabar tu discurso directamente cuando estés listo.</p>", unsafe_allow_html=True)
    recorded_file = st.camera_input("Grabar discurso")
    if recorded_file is not None:
        video_to_process = recorded_file

elif st.session_state["input_mode"] == "youtube":
    st.markdown("<p style='text-align: center; color: #9ca3af; font-size: 0.9rem;'>Pega el enlace de un discurso o presentación de YouTube:</p>", unsafe_allow_html=True)
    youtube_url = st.text_input("Enlace de YouTube", placeholder="https://www.youtube.com/watch?v=...")
    if youtube_url:
        st.info("ℹ️ Nota: Para un análisis multimodal óptimo, te recomendamos usar la opción de subir archivo o grabación directa.")

# Si hay un archivo listo para procesar: Cuadrito de video a la izquierda y botón de analizar al lado
if video_to_process is not None:
    st.markdown("<div style='margin-top: 1rem;'></div>", unsafe_allow_html=True)
    col_vid, col_btn = st.columns([1, 2])
    
    with col_vid:
        st.video(video_to_process)
        
    with col_btn:
        st.markdown("<div style='height: 20px;'></div>", unsafe_allow_html=True)
        if st.button("⚡ Iniciar Análisis con IA", key="btn_analizar"):
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

else:
    # 5 ÍTEMS PRINCIPALES DE LO QUE ANALIZA LA IA (Se muestran antes de subir el video)
    st.markdown("<div style='margin-top: 2rem;'></div>", unsafe_allow_html=True)
    st.markdown("<h3 style='text-align: center; font-size: 1.1rem; color: #9ca3af; margin-bottom: 1rem;'>¿Qué evaluará nuestra IA en tu intervención?</h3>", unsafe_allow_html=True)
    
    col_i1, col_i2, col_i3, col_i4, col_i5 = st.columns(5)
    
    with col_i1:
        st.markdown("<div style='background-color: #111827; border: 1px solid #1f2937; padding: 1rem; border-radius: 0.75rem; text-align: center; height: 110px;'><div style='font-weight: 600; font-size: 0.85rem; color: #f9fafb;'>1. Convicción Global</div><div style='font-size: 0.7rem; color: #9ca3af; margin-top: 0.4rem;'>Nivel de impacto general</div></div>", unsafe_allow_html=True)
    with col_i2:
        st.markdown("<div style='background-color: #111827; border: 1px solid #1f2937; padding: 1rem; border-radius: 0.75rem; text-align: center; height: 110px;'><div style='font-weight: 600; font-size: 0.85rem; color: #f9fafb;'>2. Lenguaje Corporal</div><div style='font-size: 0.7rem; color: #9ca3af; margin-top: 0.4rem;'>Postura y gestos de manos</div></div>", unsafe_allow_html=True)
    with col_i3:
        st.markdown("<div style='background-color: #111827; border: 1px solid #1f2937; padding: 1rem; border-radius: 0.75rem; text-align: center; height: 110px;'><div style='font-weight: 600; font-size: 0.85rem; color: #f9fafb;'>3. Voz y Tonalidad</div><div style='font-size: 0.7rem; color: #9ca3af; margin-top: 0.4rem;'>Modulación y silencios</div></div>", unsafe_allow_html=True)
    with col_i4:
        st.markdown("<div style='background-color: #111827; border: 1px solid #1f2937; padding: 1rem; border-radius: 0.75rem; text-align: center; height: 110px;'><div style='font-weight: 600; font-size: 0.85rem; color: #f9fafb;'>4. Estructura Pitch</div><div style='font-size: 0.7rem; color: #9ca3af; margin-top: 0.4rem;'>Gancho y persuasión</div></div>", unsafe_allow_html=True)
    with col_i5:
        st.markdown("<div style='background-color: #111827; border: 1px solid #1f2937; padding: 1rem; border-radius: 0.75rem; text-align: center; height: 110px;'><div style='font-weight: 600; font-size: 0.85rem; color: #f9fafb;'>5. Coaching Práctico</div><div style='font-size: 0.7rem; color: #9ca3af; margin-top: 0.4rem;'>Tácticas de mejora</div></div>", unsafe_allow_html=True)
