# Estado Actual del Proyecto - Corrector Ortotipográfico

## ✅ Funcionando Correctamente

### Infraestructura
- XML Handler con tempfile (sin errores de permisos)
- Flask web server funcionando
- Interfaz de subida de archivos
- Sistema de sesiones con pickle

### Detecciones Funcionando
1. **Ortotipografía RAE** ✅
   - Comillas inglesas → latinas
   - Guiones → rayas en diálogos
   - Espacios duros (%, unidades)
   - Puntuación con comillas

2. **Redundancias** ✅
   - "subir arriba" → "subir"
   - "completamente lleno" → "lleno"
   - +18 redundancias comunes

3. **Cosismo** ✅
   - "la cosa es que" → "el asunto es que"
   - Detección de uso vago de "cosa"

---

## ❌ Problemas Conocidos NO Resueltos

### 1. Interfaz de Revisión
**Problema**: El panel de correcciones solo muestra las primeras ~100 correcciones
**Causa**: CSS max-height limitado o problema de renderizado
**Impacto**: Usuario no puede ver/seleccionar todas las correcciones
**Estado**: INTENTADO arreglar pero persiste

### 2. Detecciones de Estilo Avanzadas
**Problema**: Voz pasiva y gerundios NO tienen corrección concreta
- Detectan: "fue revisado" 
- Sugieren: "Considere voz activa" ← NO es texto de reemplazo
**Solución aplicada**: DESHABILITADAS hasta implementar correcciones reales
**Estado**: Requiere lógica más compleja con SpaCy/LLM

### 3. Loading Indicator
**Problema**: No muestra feedback visual durante análisis (1-3 min)
**Causa**: Flask síncrono, sin WebSockets
**Workaround**: Usuario debe esperar/refrescar
**Estado**: Requiere arquitectura async (Celery/Redis)

### 4. Track Changes Color
**Problema Reportado**: Aparece en rojo en lugar de verde
**Causa**: Posible que Word ignore el color `00FF00` en Track Changes
**Estado**: Por verificar si es limitación de Word

---

## 🔧 Qué Funciona End-to-End

1. Subir documento .docx
2. Análisis de ortotipografía + redundancias + cosismo ONLY
3. Panel de revisión con categorías
4. Selección de correcciones
5. Aplicación con Track Changes
6. Descarga de documento con correcciones aplicadas

**Limitación principal**: Solo ~100-200 primeras correcciones visibles en panel

---

## 💡 Recomendaciones

### Corto plazo (usuario puede usar ahora)
- Procesar documentos por secciones (<100 págs)
- Usar solo categorías que funcionan: ortotipografía, redundancias, cosismo
- Ignorar voz pasiva hasta nueva implementación

### Mediano plazo (requiere desarrollo)
1. **Panel de correcciones**: Paginación o virtualización
2. **Voz pasiva**: Integrar LLM (GPT-4) para sugerencias concretas
3. **Loading**: Celery + progress bar real
4. **Color verde**: Investigar spec OpenXML Track Changes

---

## Archivos Clave

- `style_checker.py` - Detecciones (voz pasiva/gerundios DESHABILITADOS)
- `corrector_integrado.py` - Detector sin aplicar
- `aplicador_correcciones.py` - Aplica solo aprobadas
- `app_web.py` - Servidor Flask
- `templates/review.html` - UI de revisión (BUG: no muestra todas)
