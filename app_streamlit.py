import streamlit as st
import os
from pathlib import Path
from datetime import datetime
import time

# Importar nuestras clases de lógica (ya corregidas)
from corrector_profesional_v2 import ProfessionalCorrectorV2

# Configuración de la página
st.set_page_config(
    page_title="Corrector MBAI Native",
    page_icon="📝",
    layout="centered"
)

# Estilos CSS personalizados
st.markdown("""
    <style>
    .main {
        background-color: #f5f5f5;
    }
    .stButton>button {
        width: 100%;
        background-color: #4CAF50;
        color: white;
        height: 3em;
        border-radius: 10px;
    }
    .success-box {
        padding: 20px;
        background-color: #d4edda;
        border-color: #c3e6cb;
        color: #155724;
        border-radius: 10px;
        margin-bottom: 20px;
    }
    </style>
""", unsafe_allow_html=True)

# ---------------------------------------------------------
# CACHÉ DE RECURSOS (Para velocidad)
# ---------------------------------------------------------
@st.cache_resource
def cargar_corrector():
    """Inicializa el corrector y carga el diccionario UNA sola vez."""
    print("🚀 Iniciando corrector para Streamlit...")
    corrector = ProfessionalCorrectorV2()
    # Forzar la carga del diccionario ahora para que esté listo en caché
    if corrector.ortotipo.spell: # Accedemos al spelling checker interno si existe
         corrector.ortotipo.spell._cargar_diccionario_si_necesario()
    
    # Truco: Si ProfessionalCorrectorV2 no expone el spelling checker directamente,
    # instanciamos uno auxiliar para asegurar que la caché de Python lo tenga.
    from spelling_checker import SpellingChecker
    sp = SpellingChecker()
    sp._cargar_diccionario_si_necesario()
    
    return corrector

# ---------------------------------------------------------
# INTERFAZ
# ---------------------------------------------------------
st.title("📝 Corrector MBAI Native")
st.markdown("### Ortotipografía, Espacios y Ortografía Avanzada")
st.markdown("Sube tu documento `.docx`. El sistema aplicará correcciones RAE, eliminará espacios múltiples y revisará la ortografía usando un corpus masivo.")

# Cargar corrector (con spinner la primera vez)
with st.spinner('Cargando diccionarios (1.2M palabras)...'):
    corrector = cargar_corrector()

# Subida de archivo
uploaded_file = st.file_uploader("Elige un archivo Word (.docx)", type="docx")

if uploaded_file is not None:
    st.info(f"📄 Archivo cargado: {uploaded_file.name}")
    
    # Botón de procesar
    if st.button("🔍 Corregir Documento"):
        try:
            # Crear directorios temporales
            temp_dir = Path("temp_streamlit")
            temp_dir.mkdir(exist_ok=True)
            
            # Guardar archivo subido
            input_path = temp_dir / uploaded_file.name
            timestamp = datetime.now().strftime('%H%M%S')
            output_name = f"{input_path.stem}_CORREGIDO_{timestamp}.docx"
            output_path = temp_dir / output_name
            
            with open(input_path, "wb") as f:
                f.write(uploaded_file.getbuffer())
            
            # Procesar
            progress_bar = st.progress(0)
            status_text = st.empty()
            
            status_text.text("Analizando estructura y cargando diccionario...")
            progress_bar.progress(20)
            
            # Ejecutar corrección
            # Redirigir stdout para capturar logs si fuera necesario, 
            # pero aquí confiamos en el proceso.
            corrector.procesar_documento(str(input_path), str(output_path))
            
            progress_bar.progress(100)
            status_text.text("¡Procesamiento completado!")
            
            # Mostrar estadísticas
            st.balloons()
            
            st.markdown(f"""
            <div class="success-box">
                <h3>✅ ¡Documento Corregido!</h3>
                <p>Se han analizado ortografía, espacios y estilos.</p>
                <ul>
                    <li><b>Espacios múltiples:</b> Corregidos y unificados.</li>
                    <li><b>Ortografía:</b> Revisada con diccionario ampliado (ignora nombres propios).</li>
                    <li><b>Estilo RAE:</b> Comillas, guiones y símbolos ajustados.</li>
                </ul>
            </div>
            """, unsafe_allow_html=True)
            
            # Estadísticas (Recuperadas del objeto corrector)
            cols = st.columns(3)
            cols[0].metric("Párrafos", corrector.stats['parrafos_procesados'])
            cols[1].metric("Modificaciones", corrector.stats['parrafos_modificados'])
            cols[2].metric("Correcciones", corrector.stats['correcciones_totales'])
            
            # Botón de descarga
            with open(output_path, "rb") as f:
                st.download_button(
                    label="⬇️ Descargar Documento Corregido (Word)",
                    data=f,
                    file_name=output_name,
                    mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
                )
                
            # Limpieza (Opcional, OS se encarga eventualmente)
            # os.remove(input_path)
            
        except Exception as e:
            st.error(f"Ocurrió un error al procesar: {e}")
            st.exception(e)

# Footer
st.markdown("---")
st.caption("Desarrollado para MBAI Native - Versión 2.1 (Corpus Extendido)")
