# -*- mode: python ; coding: utf-8 -*-
"""
Spec file para crear ejecutable del Corrector Ortotipográfico RAE.
Ejecutar con: pyinstaller corrector_rae.spec
"""

import os
import sys
import spacy

# Obtener ruta del modelo SpaCy
spacy_path = os.path.dirname(spacy.__file__)

block_cipher = None

# Archivos de datos adicionales
added_files = [
    ('templates', 'templates'),
    ('static', 'static'),
    ('sessions', 'sessions'),
    # Modelo SpaCy
    (os.path.join(spacy_path, 'lang'), os.path.join('spacy', 'lang')),
]

# Buscar modelo es_core_news_sm
try:
    import es_core_news_sm
    model_path = os.path.dirname(es_core_news_sm.__file__)
    added_files.append((model_path, 'es_core_news_sm'))
except ImportError:
    print("⚠️ Modelo SpaCy es_core_news_sm no encontrado. Instálalo con:")
    print("   python -m spacy download es_core_news_sm")

a = Analysis(
    ['app_web.py'],
    pathex=[],
    binaries=[],
    datas=added_files,
    hiddenimports=[
        'spacy',
        'spacy.lang.es',
        'es_core_news_sm',
        'flask',
        'jinja2',
        'werkzeug',
        'lxml',
        'lxml.etree',
        'lxml._elementpath',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='CorrectorRAE',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=True,  # True para ver logs, False para ocultar consola
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=None,
)
