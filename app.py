import os
import time
import streamlit as st
import google.generativeai as genai
from st_supabase_connection import SupabaseConnection

# Configuración de la página
st.set_page_config(
    page_title="Gemini Speech & Persuasion AI",
    page_icon="🎙️",
    layout="centered"
)

# Estilos CSS modernos
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

# --- CONFIGURACIÓN DE SUPABASE (AUTENTICACIÓN DE USUARIOS) ---
# Nota: Asegúrate de agregar tus credenciales de Supabase en los "Secrets" de Streamlit Cloud
try:
    supabase = st.connection("supabase", type=SupabaseConnection)
except Exception:
    supabase = None

def gestionar_autenticacion():
    if "user" not in st.session_state:
        st.session_state["user"] = None

    if st.session_state["user"] is None:
        st.markdown("# 🎙️ Acceso a la Plataforma")
        tab1, tab2 = st.tabs(["🔑 Iniciar Sesión", "📝 Registrarse"])

        with tab1:
            st.subheader("Ingresa a tu cuenta")
            correo_login = st.text_input("Correo electrónico", key="login_email")
            pass_login = st.text_input("Contraseña", type="password", key="login_pass")
            
            if st.button("Entrar"):
                if supabase and correo_login and pass_login:
                    try:
                        response = supabase.auth.sign_in_with_password({"email": correo_login, "password": pass_login})
                        if response.user:
                            st.session_state["user"] = response.user.email
                            st.rerun()
                    except Exception as e:
                        st.error(f"Error al iniciar sesión: Verifícate o revisa tus credenciales.")
                else:
                    st.warning("Por favor completa todos los campos.")

        with tab2:
            st.subheader("Crea tu cuenta de alumno")
            correo_reg = st.text_input("Correo electrónico", key="reg_email")
            pass_reg = st.text_input("Crea una contraseña", type="password", key="reg_pass")
            
            if st.button("Registrarse"):
                if supabase and correo_reg and pass_reg:
                    try:
                        response = supabase.auth.sign_up({"email": correo_reg, "password": pass_reg})
                        st.success("¡Cuenta creada con éxito! Ya puedes iniciar sesión en la pestaña de al lado.")
                    except Exception as e:
                        st.error(f"No se pudo registrar el usuario. Es posible que el correo ya esté en uso.")
                else:
                    st.warning("Por favor completa todos los campos.")
        return False
    return True

if not gestionar_autenticacion():
    st.stop()

# --- APLICACIÓN PRINCIPAL (VISIBLE SOLO PARA USUARIOS LOGUEADOS) ---
API_KEY = "AIzaSyDLETiXyT5p3hrxzPBFo_UUNaIIpVUPb4U"
genai.configure(api_key=API_KEY)

col1, col2 = st.columns([8, 2])
with col1:
    st.markdown("# 🎙️ Gemini Speech & Persuasion AI")
with col2:
    if st.button("Cerrar Sesión"):
        st.session_state["user"] = None
        st.rerun()

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

                gemini_file = genai.upload_file(temp_path)
                
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
