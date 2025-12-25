# Guía Rápida de Ejecución

## 📖 Uso Básico

### 1️⃣ Modo Básico (Correcciones Aplicadas Directamente)
```bash
python main.py documento.docx
```
**Resultado**: `documento_corregido.docx` - cambios ya aplicados

### 2️⃣ Modo Profesional (Track Changes)
```bash
python main.py documento.docx --profesional
```
**Resultado**: `documento_tc.docx` - con marcas de revisión

---

## 🎯 Opciones Completas

```bash
# Con archivo de salida personalizado
python main.py documento.docx -o mi_revision.docx

# Modo profesional con autor personalizado
python main.py documento.docx -p --autor "Tu Nombre"

# Modo básico con idioma específico
python main.py documento.docx --idioma es-ES

# Ver ayuda
python main.py --help
```

---

## 🧪 Prueba Rápida

1. **Crear documento de prueba**:
```bash
python crear_prueba.py
```

2. **Modo básico**:
```bash
python main.py documento_prueba.docx
```

3. **Modo profesional**:
```bash
python main.py documento_prueba.docx -p
```

4. **Abrir en Word** el archivo generado y revisar cambios

---

## ⚡ Atajos

**Básico rápido**:
```bash
python main.py archivo.docx
```

**Profesional rápido**:
```bash
python main.py archivo.docx -p
```

**Custom todo**:
```bash
python main.py archivo.docx -p -o revision_final.docx --autor "Editor Principal"
```
