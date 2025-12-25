"""
Web App para corrección ortotipográfica con revisión interactiva.
Nuevo flujo: Analizar → Revisar → Aplicar aprobadas
"""
from flask import Flask, render_template, request, send_file, redirect, url_for, session, make_response
from werkzeug.utils import secure_filename
import os
from pathlib import Path
from datetime import datetime
import subprocess
import json
import pickle

from corrector_integrado import CorrectorIntegrado
from aplicador_correcciones import AplicadorCorrecciones

app = Flask(__name__)
app.secret_key = 'antigravity_corrector_secret_key_2024'
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['OUTPUT_FOLDER'] = 'outputs'
app.config['SESSIONS_FOLDER'] = 'sessions'
app.config['MAX_CONTENT_LENGTH'] = 50 * 1024 * 1024  # 50MB max

# Crear carpetas
for folder in [app.config['UPLOAD_FOLDER'], app.config['OUTPUT_FOLDER'], app.config['SESSIONS_FOLDER']]:
    os.makedirs(folder, exist_ok=True)

ALLOWED_EXTENSIONS = {'docx'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    """Paso 1: Subir archivo y analizarlo"""
    if 'file' not in request.files:
        return "No se seleccionó archivo", 400
    
    file = request.files['file']
    if file.filename == '' or not allowed_file(file.filename):
        return "Archivo inválido (solo .docx)", 400
    
    # Guardar archivo uploaded
    filename = secure_filename(file.filename)
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    session_id = f"{Path(filename).stem}_{timestamp}"
    
    filepath = os.path.join(app.config['UPLOAD_FOLDER'], session_id + '.docx')
    file.save(filepath)
    
    try:
        print(f"\n{'='*60}")
        print(f"ANALIZANDO: {filename}")
        print(f"{'='*60}\n")
        
        # Analizar con corrector integrado
        corrector = CorrectorIntegrado()
        correcciones_por_categoria = corrector.analizar_documento(filepath)
        
        # Guardar estado en sesión
        session_file = os.path.join(app.config['SESSIONS_FOLDER'], session_id + '.pkl')
        with open(session_file, 'wb') as f:
            pickle.dump({
                'filename': filename,
                'filepath': filepath,
                'correcciones': correcciones_por_categoria,
                'todas_correcciones': corrector.correcciones,
                'stats': corrector.stats_por_categoria
            }, f)
        
        print(f"✓ Sesión guardada: {session_id}")
        
        # Redirigir a primera página de revisión
        return redirect(f'/review/{session_id}/0')
    
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        import traceback
        traceback.print_exc()
        return f"Error al analizar: {str(e)}", 500

@app.route('/review/<session_id>/<int:page>')
def review_page(session_id, page):
    """Muestra página de revisión con correcciones agrupadas por categoría COMPLETA."""
    try:
        # Cargar sesión
        session_file = os.path.join(app.config['SESSIONS_FOLDER'], session_id + '.pkl')
        with open(session_file, 'rb') as f:
            session_data = pickle.load(f)
        
        todas_correcciones = session_data['todas_correcciones']
        
        # Obtener categorías disponibles
        corrector_temp = CorrectorIntegrado()
        
        # Agrupar TODAS las correcciones por categoría (documento completo)
        correcciones_por_categoria_completas = {}
        categorias_con_datos = []
        
        for categoria in corrector_temp.CATEGORIAS.keys():
            corrs_categoria = [c for c in todas_correcciones if c.categoria == categoria]
            if corrs_categoria:
                correcciones_por_categoria_completas[categoria] = {
                    'nombre': corrector_temp.CATEGORIAS[categoria],
                    'correcciones': corrs_categoria
                }
                categorias_con_datos.append(categoria)
        
        # Paginación POR CATEGORÍA (cada página = una categoría completa)
        total_pages = len(categorias_con_datos)
        
        if total_pages == 0:
            # No hay correcciones
            return render_template('review_paginated.html',
                                 filename=session_data['filename'],
                                 session_id=session_id,
                                 page=0,
                                 total_pages=1,
                                 total_correcciones=0,
                                 correcciones_por_categoria={},
                                 stats_totales={},
                                 categoria_actual=None,
                                 todas_categorias=[])
        
        # Asegurar página válida
        page = min(page, total_pages - 1)
        page = max(page, 0)
        
        # Categoría actual para esta página
        categoria_actual = categorias_con_datos[page]
        
        # Solo pasar la categoría de esta página
        datos_para_template = {
            categoria_actual: correcciones_por_categoria_completas[categoria_actual]
        }
        
        # Estadísticas TOTALES de todas las categorías
        stats_totales = {}
        for cat, datos in correcciones_por_categoria_completas.items():
            stats_totales[cat] = {
                'nombre': datos['nombre'],
                'total': len(datos['correcciones'])
            }
        
        return render_template('review_paginated.html',
                             filename=session_data['filename'],
                             session_id=session_id,
                             page=page,
                             total_pages=total_pages,
                             total_correcciones=len(todas_correcciones),
                             correcciones_por_categoria=datos_para_template,
                             stats_totales=stats_totales,
                             categoria_actual=corrector_temp.CATEGORIAS[categoria_actual],
                             todas_categorias=[(i, corrector_temp.CATEGORIAS[cat]) for i, cat in enumerate(categorias_con_datos)])
    
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        import traceback
        traceback.print_exc()
        return f"Error al cargar revisión: {str(e)}", 500

@app.route('/apply_corrections', methods=['POST'])
def apply_corrections():
    """Paso 2: Aplicar solo correcciones aprobadas"""
    session_id = request.form.get('session_id')
    selected_ids_json = request.form.get('selected_ids')
    
    if not session_id or not selected_ids_json:
        return "Datos faltantes", 400
    
    try:
        selected_ids = json.loads(selected_ids_json)
        selected_ids = [int(id_str) for id_str in selected_ids]
        
        # Cargar sesión
        session_file = os.path.join(app.config['SESSIONS_FOLDER'], session_id + '.pkl')
        with open(session_file, 'rb') as f:
            session_data = pickle.load(f)
        
        todas_correcciones = session_data['todas_correcciones']
        filepath = session_data['filepath']
        filename = session_data['filename']
        
        # Filtrar solo aprobadas
        correcciones_aprobadas = {}
        for corr in todas_correcciones:
            if corr.id in selected_ids:
                correcciones_aprobadas[corr.id] = {
                    'texto_original': corr.texto_original,
                    'texto_nuevo': corr.texto_nuevo,
                    'parrafo_num': corr.parrafo_num
                }
        
        print(f"\n{'='*60}")
        print(f"APLICANDO {len(correcciones_aprobadas)} CORRECCIONES")
        print(f"{'='*60}\n")
        
        # Aplicar correcciones
        output_filename = f"{Path(filename).stem}_corregido_{datetime.now().strftime('%Y%m%d_%H%M%S')}.docx"
        output_path = Path(app.config['OUTPUT_FOLDER']) / output_filename
        
        aplicador = AplicadorCorrecciones()
        aplicador.aplicar_correcciones(filepath, str(output_path), correcciones_aprobadas)
        
        # Limpiar archivos temporales
        try:
            os.remove(filepath)
            os.remove(session_file)
        except:
            pass
        
        # Descargar archivo directamente al PC del usuario
        # Usar nombre simple sin caracteres especiales para evitar problemas
        safe_filename = output_filename.encode('ascii', 'ignore').decode('ascii')
        if not safe_filename:
            safe_filename = 'documento_corregido.docx'
        
        response = make_response(send_file(
            str(output_path.absolute()),
            mimetype='application/vnd.openxmlformats-officedocument.wordprocessingml.document'
        ))
        
        # Configurar header de descarga con nombre correcto
        response.headers['Content-Disposition'] = f'attachment; filename="{safe_filename}"; filename*=UTF-8\'\'\'{output_filename}'
        response.headers['Content-Type'] = 'application/vnd.openxmlformats-officedocument.wordprocessingml.document'
        
        return response
    
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        import traceback
        traceback.print_exc()
        return f"Error al aplicar correcciones: {str(e)}", 500

if __name__ == '__main__':
    print("\n" + "="*60)
    print("🌐 CORRECTOR ORTOTIPOGRÁFICO - Versión Profesional")
    print("   Con revisión interactiva y análisis de estilo")
    print("="*60)
    print("\n🚀 Servidor iniciado en: http://localhost:5000")
    print("\n📝 Flujo:")
    print("   1. Sube documento → Análisis automático")
    print("   2. Revisa correcciones por categorías")
    print("   3. Aprueba/rechaza las que quieras")
    print("   4. Descarga con Track Changes en verde")
    print("\n⏹️  Para detener: Ctrl+C")
    print("="*60 + "\n")
    
    app.run(debug=True, port=5000)

def upload_file():
    if 'file' not in request.files:
        return "No se seleccionó archivo", 400
    
    file = request.files['file']
    if file.filename == '':
        return "Nombre de archivo vacío", 400
    
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)
        
        # Obtener modo
        modo = request.form.get('modo', 'basico')
        
        # Preparar nombre de salida CON TIMESTAMP
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        base_name = Path(filename).stem
        
        if modo == 'profesional':
            output_filename = f"{base_name}_tc_{timestamp}.docx"
        else:
            output_filename = f"{base_name}_corregido_{timestamp}.docx"
        
        # Guardar en la carpeta outputs del proyecto
        output_path = Path(app.config['OUTPUT_FOLDER']) / output_filename
        output_path_abs = output_path.absolute()
        
        try:
            print(f"\n📤 Procesando {filename} en modo {modo}...")
            print(f"📁 Guardará en: {output_path_abs}")
            
            if modo == 'profesional':
                corrector = ProfessionalCorrectorV2()
                corrector.procesar_documento(filepath, str(output_path_abs))
            else:
                corrector = BasicCorrector(usar_languagetool=False)
                corrector.procesar_documento(filepath, str(output_path_abs))
                corrector.cerrar()
            
            print(f"✅ Procesamiento completado!")
            
            # Verificar que el archivo se creó
            if not output_path_abs.exists():
                return "Error: No se pudo generar el archivo corregido", 500
            
            # Limpiar archivo temporal subido
            if os.path.exists(filepath):
                os.remove(filepath)
            
            # Abrir explorador de archivos en la ubicación del archivo
            try:
                subprocess.run(['explorer', '/select,', str(output_path_abs)], check=False)
            except:
                pass  # Si falla, no es crítico
            
            # Devolver página de éxito con ubicación del archivo
            carpeta_outputs = output_path_abs.parent.absolute()
            return f"""
            <!DOCTYPE html>
            <html lang="es">
            <head>
                <meta charset="UTF-8">
                <meta name="viewport" content="width=device-width, initial-scale=1.0">
                <title>Corrección Completada</title>
                <style>
                    body {{
                        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                        min-height: 100vh;
                        display: flex;
                        align-items: center;
                        justify-content: center;
                        padding: 20px;
                    }}
                    .success-box {{
                        background: white;
                        border-radius: 20px;
                        box-shadow: 0 20px 60px rgba(0,0,0,0.3);
                        padding: 40px;
                        max-width: 600px;
                        text-align: center;
                    }}
                    .check {{
                        font-size: 80px;
                        color: #4CAF50;
                        margin-bottom: 20px;
                    }}
                    h1 {{
                        color: #333;
                        margin-bottom: 20px;
                    }}
                    .file-path {{
                        background: #f5f5f5;
                        padding: 15px;
                        border-radius: 10px;
                        margin: 20px 0;
                        font-family: monospace;
                        word-break: break-all;
                        color: #667eea;
                        font-weight: bold;
                    }}
                    .btn {{
                        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                        color: white;
                        padding: 15px 40px;
                        border: none;
                        border-radius: 30px;
                        font-size: 1.1em;
                        cursor: pointer;
                        text-decoration: none;
                        display: inline-block;
                        margin-top: 20px;
                    }}
                    .btn:hover {{
                        transform: scale(1.05);
                    }}
                    .info {{
                        color: #666;
                        margin-top: 20px;
                        font-size: 0.9em;
                    }}
                </style>
            </head>
            <body>
                <div class="success-box">
                    <div class="check">✅</div>
                    <h1>¡Corrección Completada!</h1>
                    <p>Tu documento ha sido procesado exitosamente.</p>
                    
                    <div class="file-path">
                        📄 {output_filename}
                    </div>
                    
                    <p><strong>Ubicación:</strong><br>{carpeta_outputs}</p>
                    
                    <div class="info">
                        El archivo está en la carpeta "outputs" del proyecto.<br>
                        La ventana del explorador se abrió automáticamente.<br>
                        Ábrelo con Microsoft Word para ver las correcciones.
                    </div>
                    
                    <a href="/" class="btn">Corregir Otro Documento</a>
                </div>
            </body>
            </html>
            """
            
        except Exception as e:
            print(f"❌ Error: {str(e)}")
            import traceback
            traceback.print_exc()
            
            # Limpiar archivo subido
            if os.path.exists(filepath):
                os.remove(filepath)
            
            return f"Error al procesar: {str(e)}", 500
    
    return "Tipo de archivo no permitido (solo .docx)", 400


if __name__ == '__main__':
    print("\n" + "="*60)
    print("🌐 CORRECTOR ORTOTIPOGRÁFICO - Web Interface")
    print("="*60)
    print("\n🚀 Servidor iniciado en: http://localhost:5000")
    print("\n📝 Instrucciones:")
    print("   1. Abre tu navegador en http://localhost:5000")
    print("   2. Sube tu archivo .docx")
    print("   3. Elige modo (Básico o Profesional)")
    print("   4. Descarga el archivo corregido")
    print("\n⏹️  Para detener: Ctrl+C")
    print("="*60 + "\n")
    
    app.run(debug=True, port=5000)
