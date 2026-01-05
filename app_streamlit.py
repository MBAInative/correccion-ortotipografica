import streamlit as st
import os
from pathlib import Path
from datetime import datetime
import pandas as pd
import difflib

# Importar lógica de corrección avanzada
from corrector_integrado import CorrectorIntegrado
from aplicador_correcciones import AplicadorCorrecciones

# Configuración de la página
st.set_page_config(
    page_title="Corrector MBAI Native",
    page_icon="📝",
    layout="wide"
)

# Estilos CSS para el Diff (Rojo/Verde)
st.markdown("""
    <style>
    .diff-container {
        display: flex;
        gap: 10px;
        font-family: 'Segoe UI', sans-serif;
    }
    .diff-box {
        flex: 1;
        padding: 10px;
        border-radius: 5px;
        border: 1px solid #eee;
        background-color: white;
        min-height: 40px;
        line-height: 1.5;
    }
    .del {
        background-color: #ffdada;
        color: #b01011;
        text-decoration: line-through;
        padding: 0 2px;
    }
    .ins {
        background-color: #e1ffd1;
        color: #008000;
        font-weight: bold;
        padding: 0 2px;
    }
    .cat-badge {
        font-size: 0.8em;
        padding: 2px 8px;
        border-radius: 10px;
        background-color: #667eea;
        color: white;
        margin-bottom: 5px;
        display: inline-block;
    }
    .metric-card {
        background-color: white;
        padding: 15px;
        border-radius: 10px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
        text-align: center;
        border-bottom: 3px solid #667eea;
    }
    </style>
""", unsafe_allow_html=True)

# ---------------------------------------------------------
# FUNCIONES DE APOYO
# ---------------------------------------------------------
@st.cache_resource
def cargar_corrector_completo():
    """Carga el motor integrado con todas las reglas y diccionarios."""
    corrector = CorrectorIntegrado()
    # Asegurar que el diccionario masivo esté cargado
    if corrector.spelling and hasattr(corrector.spelling, '_cargar_diccionario_si_necesario'):
        corrector.spelling._cargar_diccionario_si_necesario()
    return corrector

def get_diff_html(old, new):
    """Genera HTML resaltado para mostrar diferencias."""
    result_old = ""
    result_new = ""
    
    s = difflib.SequenceMatcher(None, old, new)
    for tag, i1, i2, j1, j2 in s.get_opcodes():
        if tag == 'replace':
            result_old += f'<span class="del">{old[i1:i2]}</span>'
            result_new += f'<span class="ins">{new[j1:j2]}</span>'
        elif tag == 'delete':
            result_old += f'<span class="del">{old[i1:i2]}</span>'
        elif tag == 'insert':
            result_new += f'<span class="ins">{new[j1:j2]}</span>'
        elif tag == 'equal':
            result_old += old[i1:i2]
            result_new += new[j1:j2]
            
    return result_old, result_new

# ---------------------------------------------------------
# INTERFAZ PRINCIPAL
# ---------------------------------------------------------
# Encabezado con Logo y Título
header_col1, header_col2 = st.columns([1, 5])
with header_col1:
    if os.path.exists("Icono. MBAInative.02.png"):
        st.image("Icono. MBAInative.02.png", width=120)

with header_col2:
    st.title("Corrector MBAI Native")
    st.markdown("### Revisión Interactiva por Apartados")

st.markdown("---")

# Barra lateral con información
with st.sidebar:
    if os.path.exists("Icono. MBAInative.02.png"):
        st.image("Icono. MBAInative.02.png", width=150)
    st.markdown("### Configuración")
    modo_revisión = st.checkbox("Mostrar depuración XML", value=False)
    
    corrector = cargar_corrector_completo()
    
    if corrector.spelling.habilitado:
        st.success("✅ Diccionario Maestro Activo")
    else:
        st.warning("⚠️ Diccionario Limitado")

# 1. CARGA DE ARCHIVO
uploaded_file = st.file_uploader("Sube tu documento .docx", type="docx")

if uploaded_file:
    # Guardar temporalmente
    temp_dir = Path("temp_streamlit")
    temp_dir.mkdir(exist_ok=True)
    input_path = temp_dir / uploaded_file.name
    with open(input_path, "wb") as f:
        f.write(uploaded_file.getbuffer())

    if st.button("🔍 Iniciar Análisis Completo"):
        with st.spinner("Analizando por categorías (Ortografía, Tipografía, Estilo)..."):
            # Analizar
            correcciones_por_cat = corrector.analizar_documento(str(input_path))
            
            # Guardar en sesión
            st.session_state['correcciones_por_cat'] = correcciones_por_cat
            st.session_state['stats'] = corrector.stats_por_categoria
            st.session_state['total_correcciones'] = len(corrector.correcciones)
            st.session_state['archivo_original'] = str(input_path)
            st.session_state['todas_correcciones'] = corrector.correcciones

# 2. MOSTRAR RESULTADOS (Si existen)
if 'correcciones_por_cat' in st.session_state:
    stats = st.session_state['stats']
    total = st.session_state['total_correcciones']
    
    # --- RESUMEN POR APARTADOS ---
    st.markdown("## 📊 Resumen de Errores")
    
    # Filtrar categorías con errores
    cat_activas = {k: v for k, v in stats.items() if v > 0}
    
    if not cat_activas:
        st.success("🌟 ¡Increíble! No se han detectado errores en ninguna categoría.")
    else:
        # Mostrar métricas en columnas
        cols = st.columns(min(len(cat_activas), 4))
        for i, (cat_id, count) in enumerate(cat_activas.items()):
            nombre_cat = corrector.CATEGORIAS.get(cat_id, cat_id)
            with cols[i % 4]:
                st.markdown(f"""
                <div class="metric-card">
                    <small>{nombre_cat}</small>
                    <h2 style="margin:0; color:#667eea;">{count}</h2>
                </div>
                """, unsafe_allow_html=True)
        
        st.markdown("---")
        
        # --- LISTA DETALLADA CON COLORES ---
        st.markdown("## 🔍 Revisión Detallada")
        
        for cat_id, corrs in st.session_state['correcciones_por_cat'].items():
            if not corrs:
                continue
                
            nombre_cat = corrector.CATEGORIAS.get(cat_id, cat_id)
            with st.expander(f"📂 {nombre_cat} ({len(corrs)} detecciones)", expanded=True):
                
                for idx, c in enumerate(corrs):
                    # Generar HTML con colores
                    html_old, html_new = get_diff_html(c.texto_original, c.texto_nuevo)
                    
                    st.markdown(f"""
                    <div style="margin-bottom: 20px; border-bottom: 1px solid #f0f0f0; padding-bottom: 10px;">
                        <div class="cat-badge">Sugerencia {idx+1}</div>
                        <p style="font-size: 0.9em; color: #666; margin-bottom: 5px;"><i>{c.explicacion}</i></p>
                        <div class="diff-container">
                            <div class="diff-box">{html_old}</div>
                            <div style="display: flex; align-items: center;"> ➡️ </div>
                            <div class="diff-box">{html_new}</div>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)

        # --- DESCARGA FINAL ---
        st.markdown("---")
        st.markdown("## 💾 Paso Final")
        
        if st.button("🔨 Generar Archivo Final con Control de Cambios"):
            with st.spinner("Generando Word con revisiones marcadas..."):
                input_path = st.session_state['archivo_original']
                timestamp = datetime.now().strftime('%H%M%S')
                output_name = f"{Path(input_path).stem}_CORREGIDO_{timestamp}.docx"
                output_path = Path("temp_streamlit") / output_name
                
                # Para el archivo final, aplicamos TODAS las correcciones detectadas
                # Usamos el AplicadorCorrecciones que ya existe
                aplicador = AplicadorCorrecciones()
                
                # Convertir lista de objetos a diccionario para el aplicador
                dict_aprobadas = {}
                for c in st.session_state['todas_correcciones']:
                    dict_aprobadas[c.id] = {
                        'texto_original': c.texto_original,
                        'texto_nuevo': c.texto_nuevo,
                        'parrafo_num': c.parrafo_num
                    }
                
                aplicador.aplicar_correcciones(input_path, str(output_path), dict_aprobadas)
                
                with open(output_path, "rb") as f:
                    st.download_button(
                        label="⬇️ Descargar Documento Corregido",
                        data=f,
                        file_name=output_name,
                        mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
                    )

st.sidebar.markdown("---")
st.sidebar.caption("MBAI Native AI-Corrector v2.2")
