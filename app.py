import os
import time
import streamlit as st
import google.generativeai as genai

# Configuración de la página
st.set_page_config(
    page_title="Gemini Speech & Persuasion AI",
    page_icon="🎙️",
    layout="centered"
)

# Estilos CSS
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
    .stButton>button:hover { opacity: 0.9; }
</style>
""", unsafe_allow_html=True)

# --- SISTEMA DE CONTRASEÑA (INTEGRADO CON HOTMART) ---
PASSWORD_CORRECTA = "tu_clave_secreta_123"  # Cambia esto por la contraseña que darás en Hotmart

def check_password():
    def password_entered():
        if st.session_state["password"] == PASSWORD_CORRECTA:
            st.session_state["password_correct"] = True
            del st.session_state["password"]
        else:
            st.session_state["password_correct"] = False

    if "password_correct" not in st.session_state:
        st.markdown("# 🔒 Acceso Restringido")
        st.markdown("Por favor, ingresa la contraseña de acceso que recibiste al comprar el programa en Hotmart.")
        st.text_input("Contraseña de acceso:", type="password", on_change=password_entered, key="password")
        return False
    elif not st.session_state["password_correct"]:
        st.markdown("# 🔒 Acceso Restringido")
        st.text_input("Contraseña de acceso:", type="password", on_change=password_entered, key="password")
        st.error("😕 Contraseña incorrecta. Inténtalo de nuevo.")
        return False
    else:
        return True

if not check_password():
    st.stop()
# ----------------------------------------------------

API_KEY = "AIzaSyDLETiXyT5p3hrxzPBFo_UUNaIIpVUPb4U"
genai.configure(api_key=API_KEY)

st.markdown("# 🎙️ Gemini Speech & Persuasion AI")
st.markdown("### Simulador avanzado de oratoria, lenguaje corporal, modulación tonal y energía.")
st.divider()

st.markdown("### 📥 Sube tu Discurso en Video")
video_file = st.file_uploader("Sube tu archivo de video (.mp4, .mov, .webm)", type=["mp4", "mov", "webm"])

if video_file is not None:
    st.video(video_file)
    
    if st.button("⚡ Iniciar Análisis con IA"):
        with st.spinner("⏳ Subiendo video y analizando con Gemini..."):
            gemini_file = None
            try:
                temp_path = os.path.join("/tmp", video_file.name)
                with open(temp_path, "wb") as f:
                    f.write(video_file.getbuffer())

                # Subir archivo usando File API de Gemini
                gemini_file = genai.upload_file(temp_path)
                
                # Esperar a que esté activo
                while gemini_file.state.name == "PROCESSING":
                    time.sleep(2)
                    gemini_file = genai.get_file(gemini_file.name)
                    
                if gemini_file.state.name != "ACTIVE":
                    raise Exception("El archivo no pudo ser procesado.")

                model = genai.GenerativeModel('gemini-2.5-flash')
                
                prompt = """
                Actúa como un estricto y experto coach de oratoria ejecutiva. 
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
    st.info("💡 Sube un video de tus prácticas de 30 segundos para comenzar la evaluación.")
