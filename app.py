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

# Estilos CSS avanzados para eliminar márgenes superiores y unificar la estética limpia
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
    
    .stApp {
        background-color: #030712;
        color: #f3f4f6;
        font-family: 'Inter', sans-serif;
    }
    
    /* Eliminar padding superior predeterminado de Streamlit para subir el contenido */
    .block-container {
        padding-top: 1.5rem !important;
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
    
    /* Estilo para los File Uploaders y contenedores interactivos */
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
</style>
""", unsafe_allow_html=True)

# ⚠️ COLOCA AQUÍ TU API KEY DE GOOGLE AI STUDIO
API_KEY = "PEGA_AQUI_TU_NUEVA_API_KEY"
genai.configure(api_key=API_KEY)

# Título y Subtítulo pegados arriba sin espacios sobrantes
st.markdown("""
<div style="text-align: center; max-width: 48rem; margin: 0 auto 1.5rem auto;">
    <h2 style="font-size: 2rem; font-weight: 800; letter-spacing: -0.025em; margin-bottom: 0.5rem;">Evalúa tu oratoria con precisión de experto</h2>
    <p style="color: #9ca3af; font-size: 0.95rem;">Sube un video de tu intervención para calcular automáticamente las marcas de tiempo exactas según su duración real.</p>
</div>
""", unsafe_allow_html=True)

# Sección de Carga de Archivo visible de inmediato
video_file = st.file_uploader("Arrastra tu video aquí o explora archivos", type=["mp4", "mov", "webm"])

if video_file is not None:
    st.video(video_file)
    
    if st.button("⚡ Iniciar Análisis con IA"):
        with st.spinner("⏳ Subiendo video y analizando con Gemini..."):
            gemini_file = None
            try:
                temp_path = os.path.join("/tmp", video_file.name)
                with open(temp_path, "wb") as f:
                    f.write(video_file.getbuffer())

                gemini_file = genai.upload_file(temp_path)
                
                while gemini_file.state.name == "PROCESSING":
                    time.sleep(2)
                    gemini_file = genai.get_file(gemini_file.name)
                    
                if gemini_file.state.name != "ACTIVE":
                    raise Exception("El archivo no pudo ser procesado.")

                model = genai.GenerativeModel('gemini-2.5-flash')
                
                prompt = """
                Actúa como un estricto y experto coach de oratoria ejecutiva de Cuarto Espacio. 
                Analiza detalladamente este video y entrégame un reporte estructurado y elegante evaluando tres pilares de mejora inmediata:
                1. 🦾 **Lenguaje Corporal y Postura:** Gestos de manos, apertura de hombros y expresión facial.
                2. 🎵 **Variación de Tonalidad:** Modulación de voz, inflexiones y uso de pausas enfáticas.
                3. ⚡ **Nivel de Energía y Proyección:** Fuerza, dinamismo y convicción al transmitir el mensaje.
                """
                
                response = model.generate_content([gemini_file, prompt])
                
                st.markdown("### 📊 Reporte del Coach Gemini")
                st.markdown(response.text)
                
            except Exception as e:
                st.error(f"❌ Error de procesamiento: {str(e)}")
                
            finally:
                if gemini_file:
                    try:
                        genai.delete_file(gemini_file.name)
                    except:
                        pass
