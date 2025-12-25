"""
Script para crear ejecutable con PyInstaller.
Incluye configuración específica para SpaCy y Flask.
"""
import subprocess
import sys
import os
import shutil

def build_exe():
    print("=" * 50)
    print("🔨 Construyendo Corrector RAE .exe")
    print("=" * 50)
    
    # Limpiar builds anteriores
    for dir_name in ['build', 'dist']:
        if os.path.exists(dir_name):
            print(f"🧹 Limpiando {dir_name}/...")
            shutil.rmtree(dir_name)
    
    # Crear carpetas necesarias
    for dir_name in ['static', 'sessions']:
        os.makedirs(dir_name, exist_ok=True)
    
    # Obtener ruta del modelo SpaCy
    try:
        import spacy
        import es_core_news_sm
        spacy_data = os.path.dirname(spacy.__file__)
        model_path = os.path.dirname(es_core_news_sm.__file__)
        print(f"✓ Modelo SpaCy encontrado: {model_path}")
    except ImportError as e:
        print(f"❌ Error: {e}")
        print("Instala el modelo con: python -m spacy download es_core_news_sm")
        return False
    
    # Comando PyInstaller con todas las opciones necesarias
    cmd = [
        sys.executable, '-m', 'PyInstaller',
        '--noconfirm',
        '--onedir',  # Un directorio (más fácil de depurar que onefile)
        '--console',  # Mostrar consola para ver logs
        '--name=CorrectorRAE',
        
        # Datos adicionales
        f'--add-data=templates{os.pathsep}templates',
        f'--add-data=static{os.pathsep}static',
        f'--add-data=sessions{os.pathsep}sessions',
        f'--add-data={model_path}{os.pathsep}es_core_news_sm',
        
        # Hidden imports para SpaCy y dependencias
        '--hidden-import=spacy',
        '--hidden-import=spacy.lang.es',
        '--hidden-import=spacy.pipeline',
        '--hidden-import=es_core_news_sm',
        '--hidden-import=thinc',
        '--hidden-import=thinc.api',
        '--hidden-import=cymem',
        '--hidden-import=preshed',
        '--hidden-import=blis',
        '--hidden-import=murmurhash',
        '--hidden-import=wasabi',
        '--hidden-import=srsly',
        '--hidden-import=catalogue',
        '--hidden-import=typer',
        '--hidden-import=pathy',
        '--hidden-import=smart_open',
        '--hidden-import=flask',
        '--hidden-import=jinja2',
        '--hidden-import=werkzeug',
        '--hidden-import=lxml',
        '--hidden-import=lxml.etree',
        '--hidden-import=lxml._elementpath',
        
        # Coleccionar datos de SpaCy
        '--collect-data=spacy',
        '--collect-data=es_core_news_sm',
        '--collect-data=thinc',
        
        # Copiar binarios de SpaCy
        '--collect-binaries=spacy',
        '--collect-binaries=thinc',
        '--collect-binaries=blis',
        
        # Archivo principal
        'app_web.py',
    ]
    
    print("\n📦 Ejecutando PyInstaller...")
    print("Esto puede tardar varios minutos...\n")
    
    result = subprocess.run(cmd, capture_output=False)
    
    if result.returncode == 0:
        print("\n" + "=" * 50)
        print("✅ ¡ÉXITO! Ejecutable creado en: dist/CorrectorRAE/")
        print("=" * 50)
        print("\nPara distribuir:")
        print("1. Comprime la carpeta dist/CorrectorRAE")
        print("2. Tu amigo debe descomprimir y ejecutar CorrectorRAE.exe")
        print("3. Abrir navegador en http://localhost:5000")
        return True
    else:
        print("\n❌ Error durante la construcción")
        return False

if __name__ == '__main__':
    build_exe()
