import os
import time
import unicodedata
import streamlit as st
from google import genai

# Configuración de la página en modo oscuro
st.set_page_config(
    page_title="Gemini Speech & Persuasion AI",
    page_icon="🎙️",
    layout="centered"
)

# Estilos CSS personalizados para mantener la estética SaaS moderna
st.markdown("""
<style>
    .stApp { background-color: #020617; color: #f8fafc; }
    h1, h2, h3 { color: #f8fafc !important; }
    .stButton>button {
        background: linear-gradient(to right, #6366f1, #8b5cf6);
        color: white;
        border: none;
        border-radius: 0.75rem;
        font-weight: 600;
        width: 100%;
        padding: 0.6rem;
    }
    .stButton>button:hover {
        opacity: 0.9;
    }
</style>
""", unsafe_allow_html=True)

API_KEY = "AIzaSyDLETiXyT5p3hrxzPBFo_UUNaIIpVUPb4U"
client = genai.Client(api_key=API_KEY)

def limpiar_nombre(nombre):
    nfkd_form = unicodedata.normalize('NFKD', nombre)
    return "".join([c for c in nfkd_form if not unicodedata.combining(c)])

# Cabecera
st.markdown("# 🎙️ Gemini Speech & Persuasion AI")
st.markdown("### Simulador avanzado de oratoria, lenguaje corporal, modulación tonal y energía.")
st.divider()

# Sección de Carga de Video
st.markdown("### 📥 Sube tu Discurso en Video")
video_file = st.file_uploader("Sube tu archivo de video (.mp4, .mov, .webm)", type=["mp4", "mov", "webm"])

if video_file is not None:
    st.video(video_file)
    
    if st.button("⚡ Iniciar Análisis con IA"):
        with st.spinner("⏳ Subiendo video y analizando con Gemini (esto puede tomar unos segundos)..."):
            gemini_file = None
            try:
                # Guardar temporalmente el archivo subido
                temp_path = os.path.join("/tmp", limpiar_nombre(video_file.name))
                with open(temp_path, "wb") as f:
                    f.write(video_file.getbuffer())

                # Subir a Gemini
                gemini_file = client.files.upload(file=temp_path)
                
                # Esperar estado activo
                while gemini_file.state.name == "PROCESSING":
                    time.sleep(2)
                    gemini_file = client.files.get(name=gemini_file.name)
                    
                if gemini_file.state.name != "ACTIVE":
                    raise Exception("El archivo no pudo ser procesado por los servidores.")

                prompt = """
                Actúa como un estricto y experto coach de oratoria ejecutiva. 
                Analiza detalladamente este video y entrégame un reporte estructurado, limpio y elegante evaluando estrictamente tres pilares de mejora inmediata:
                1. 🦾 **Lenguaje Corporal y Postura:** Gestos de manos, apertura de hombros, expresión facial y contacto visual.
                2. 🎵 **Variación de Tonalidad:** Modulación de voz, inflexiones y uso de pausas enfáticas frente a monotonía.
                3. ⚡ **Nivel de Energía y Proyección:** Fuerza, dinamismo y convicción al transmitir el mensaje.

                Usa un tono profesional, directo, constructivo y señala específicamente qué corregir.
                """
                
                response = client.models.generate_content(
                    model='gemini-2.5-flash',
                    contents=[gemini_file, prompt]
                )
                
                st.markdown("### 📊 Reporte del Coach Gemini")
                st.markdown(response.text)
                
            except Exception as e:
                st.error(f"❌ Error de procesamiento: {str(e)}")
                
            finally:
                if gemini_file:
                    try:
                        client.files.delete(name=gemini_file.name)
                    except:
                        pass
else:
    st.info("💡 Sube un video de tus prácticas de 30 segundos para comenzar la evaluación.")
