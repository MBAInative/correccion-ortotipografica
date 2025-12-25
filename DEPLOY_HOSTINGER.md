# Despliegue en Hostinger cPanel - Guía Paso a Paso

## Archivos necesarios para subir

Sube estos archivos a la carpeta de tu aplicación:

```
├── app_web.py
├── corrector_integrado.py
├── ortotipografia_v3.py
├── style_checker_v2.py
├── spelling_checker.py
├── xml_handler.py
├── aplicador_correcciones.py
├── passenger_wsgi.py          ← WSGI entry point
├── requirements.txt           ← Dependencias
├── templates/
│   ├── index.html
│   ├── review_paginated.html
│   └── ... (otras plantillas)
├── sessions/                  ← Crear vacía
└── uploads/                   ← Crear vacía
```

## Pasos en cPanel

### 1. Accede a cPanel
- Ve a tu panel de Hostinger
- Busca "Setup Python App" en la sección Software

### 2. Crea nueva aplicación Python
```
Python version:     3.9 (o superior)
Application root:   corrector (o el nombre que quieras)
Application URL:    corrector.tudominio.com
Application startup file: passenger_wsgi.py
Application Entry point:  application
```

### 3. Sube los archivos
- Usa File Manager o FTP
- Sube todo a la carpeta `corrector/`

### 4. Instala dependencias
En la interfaz de Python App:
1. Añade `requirements.txt` en "Configuration files"
2. Click "Run Pip Install"

### 5. Instala el modelo SpaCy
Si tienes acceso SSH:
```bash
source /home/tu_usuario/virtualenv/corrector/bin/activate
python -m spacy download es_core_news_sm
```

Si NO tienes SSH, añade esto a requirements.txt:
```
https://github.com/explosion/spacy-models/releases/download/es_core_news_sm-3.7.0/es_core_news_sm-3.7.0-py3-none-any.whl
```

### 6. Reinicia la aplicación
Click en "Restart" en la interfaz de Python App

### 7. Accede
Visita: https://corrector.tudominio.com

---

## Solución de problemas

### Error 500
- Revisa los logs en cPanel → Error Log
- Verifica que passenger_wsgi.py tiene `application` (no `app`)

### SpaCy no carga
- El modelo puede tardar 30-60 segundos en la primera carga
- Si falla por memoria, contacta a Hostinger para aumentar límites

### Permisos
- Asegura que `sessions/` y `uploads/` tienen permisos 755
