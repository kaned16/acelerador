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

# Estilos CSS avanzados basados en la estética oscura, moderna y minimalista solicitada
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
    
    .stApp {
        background-color: #030712;
        color: #f3f4f6;
        font-family: 'Inter', sans-serif;
    }
    
    /* Ocultar elementos predeterminados de Streamlit que rompen la estética limpia */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    
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

# Configuración de la API Key de Gemini
API_KEY = "AIzaSyDLETiXyT5p3hrxzPBFo_UUNaIIpVUPb4U"
genai.configure(api_key=API_KEY)

# Header Superior Estilizado
st.markdown("""
<div style="display: flex; align-items: center; justify-content: space-between; padding-bottom: 1.5rem; border-bottom: 1px solid #1f2937; margin-bottom: 1.5rem;">
    <div style="display: flex; align-items: center; gap: 0.75rem;">
        <div style="width: 2.5rem; height: 2.5rem; border-radius: 0.75rem; background: linear-gradient(to top right, #7c3aed, #818cf8); display: flex; align-items: center; justify-content: center; box-shadow: 0 10px 15px -3px rgba(124, 58, 237, 0.3);">
            ✨
        </div>
        <div>
            <h1 style="font-size: 1.125rem; font-weight: bold; margin: 0; background: linear-gradient(to right, #ffffff, #9ca3af, #a78bfa); -webkit-background-clip: text; -webkit-text-fill-color: transparent;">Cuarto Espacio | Oratoria AI</h1>
            <p style="font-size: 0.75rem; color: #9ca3af; margin: 0;">Análisis Multimodal de Discursos, Gestos y Persuasión</p>
        </div>
    </div>
    <div>
        <span style="display: inline-flex; align-items: center; padding: 0.25rem 0.75rem; border-radius: 9999px; font-size: 0.75rem; font-weight: 500; background-color: rgba(16, 185, 129, 0.1); color: #34d399; border: 1px solid rgba(16, 185, 129, 0.2);">
            <span style="width: 0.375rem; height: 0.375rem; border-radius: 9999px; background-color: #34d399; margin-right: 0.375rem; display: inline-block;"></span>
            API Gemini Conectada
        </span>
    </div>
</div>
""", unsafe_allow_html=True)

# Título y Subtítulo compactos (sin la etiqueta superior)
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
else:
    st.markdown("""
    <div style="background-color: #111827; border: 1px solid #1f2937; border-radius: 1rem; padding: 1rem; display: flex; align-items: center; justify-content: space-between; max-width: 48rem; margin: 1.5rem auto 0 auto;">
        <div>
            <div style="font-size: 0.75rem; font-weight: 600; color: #d1d5db;">¿Deseas probar una demostración inmediata?</div>
            <div style="font-size: 0.6875rem; color: #6b7280;">Carga un video de prueba con sincronización perfecta</div>
        </div>
        <span style="background-color: #1f2937; color: #e5e7eb; font-size: 0.75rem; font-weight: 600; padding: 0.4rem 0.8rem; border-radius: 0.75rem; border: 1px solid #374151;">
            Sube un video arriba 👆
        </span>
    </div>
    """, unsafe_allow_html=True)
