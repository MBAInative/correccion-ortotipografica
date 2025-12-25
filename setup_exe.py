"""
Setup script para cx_Freeze.
Ejecutar con: python setup_exe.py build
"""
import sys
from cx_Freeze import setup, Executable
import os

# Dependencias que cx_Freeze debe incluir
build_exe_options = {
    "packages": [
        "flask",
        "jinja2", 
        "werkzeug",
        "lxml",
        "lxml.etree",
        "spacy",
        "spacy.lang.es",
        "es_core_news_sm",
        "thinc",
        "pickle",
        "json",
        "re",
        "datetime",
        "pathlib",
        "tempfile",
        "shutil",
        "copy",
    ],
    "includes": [
        "spacy.pipeline",
        "spacy.vocab",
        "spacy.lang.es",
    ],
    "include_files": [
        ("templates", "templates"),
        ("sessions", "sessions"),
    ],
    "excludes": [
        "tkinter",
        "unittest",
        "test",
    ],
}

# Obtener ruta del modelo SpaCy y añadirlo
try:
    import es_core_news_sm
    model_path = os.path.dirname(es_core_news_sm.__file__)
    build_exe_options["include_files"].append((model_path, "es_core_news_sm"))
    print(f"✓ Modelo SpaCy incluido: {model_path}")
except ImportError:
    print("⚠️ Modelo SpaCy no encontrado")

base = None

executables = [
    Executable(
        "app_web.py",
        base=base,
        target_name="CorrectorRAE.exe",
        icon=None,
    )
]

setup(
    name="CorrectorRAE",
    version="0.1",
    description="Corrector Ortotipográfico RAE",
    author="Luis Benedicto Tuzón",
    options={"build_exe": build_exe_options},
    executables=executables,
)
