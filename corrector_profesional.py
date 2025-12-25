"""
Corrector profesional con Track Changes.
Fase 2: Genera marcas de revisión en lugar de aplicar correcciones directamente.
"""
from xml_handler import DocxXMLHandler, TrackChangesHandler, NAMESPACES
from ortotipografia import OrtotipografiaRules
from lxml import etree
from typing import List, Tuple, Dict
import re


class Correccion:
    """Representa una corrección a aplicar."""
    
    def __init__(self, tipo: str, posicion: int, longitud: int, 
                 texto_original: str, texto_nuevo: str, confianza: float = 1.0):
        """
        Args:
            tipo: 'reemplazo', 'insercion', 'eliminacion'
            posicion: Posición en el texto
            longitud: Longitud del texto a cambiar
            texto_original: Texto original
            texto_nuevo: Texto de reemplazo
            confianza: Nivel de confianza (0.0-1.0)
        """
        self.tipo = tipo
        self.posicion = posicion
        self.longitud = longitud
        self.texto_original = texto_original
        self.texto_nuevo = texto_nuevo
        self.confianza = confianza


class ProfessionalCorrector:
    """Corrector profesional con Track Changes."""
    
    def __init__(self, autor: str = "Antigravity Corrector"):
        """
        Inicializa el corrector profesional.
        
        Args:
            autor: Nombre del autor para Track Changes
        """
        self.autor = autor
        self.ortotipo = OrtotipografiaRules()
        self.stats = {
            'correcciones_totales': 0,
            'inserciones': 0,
            'eliminaciones': 0,
            'parrafos_procesados': 0
        }
    
    def detectar_correcciones_ortotipo(self, texto: str) -> List[Correccion]:
        """
        Detecta correcciones ortotipográficas necesarias.
        
        Args:
            texto: Texto a analizar
            
        Returns:
            Lista de correcciones
        """
        correcciones = []
        
        # 1. Comillas inglesas curvas -> latinas (más común)
        for match in re.finditer(r'"([^"]+)"', texto):
            correcciones.append(Correccion(
                tipo='reemplazo',
                posicion=match.start(),
                longitud=match.end() - match.start(),
                texto_original=match.group(0),
                texto_nuevo=f'{self.ortotipo.COMILLA_LATINA_ABRE}{match.group(1)}{self.ortotipo.COMILLA_LATINA_CIERRA}',
                confianza=1.0
            ))
        
        # 2. Comillas rectas -> latinas
        for match in re.finditer(r'"([^"]+)"', texto):
            correcciones.append(Correccion(
                tipo='reemplazo',
                posicion=match.start(),
                longitud=match.end() - match.start(),
                texto_original=match.group(0),
                texto_nuevo=f'{self.ortotipo.COMILLA_LATINA_ABRE}{match.group(1)}{self.ortotipo.COMILLA_LATINA_CIERRA}',
                confianza=1.0
            ))
        
        # 3. Puntuación ANTES de comillas -> DESPUÉS (RAE)
        # Buscar: .,;: antes de comilla de cierre
        for match in re.finditer(r'([.,;:])([»"\'])', texto):
            correcciones.append(Correccion(
                tipo='reemplazo',
                posicion=match.start(),
                longitud=match.end() - match.start(),
                texto_original=match.group(0),
                texto_nuevo=f'{match.group(2)}{match.group(1)}',
                confianza=1.0
            ))
        
        # 4. Guiones -> rayas (inicio de párrafo o después de espacio)
        for match in re.finditer(r'(^|\s)-\s+', texto, re.MULTILINE):
            correcciones.append(Correccion(
                tipo='reemplazo',
                posicion=match.start(),
                longitud=match.end() - match.start(),
                texto_original=match.group(0),
                texto_nuevo=f'{match.group(1)}{self.ortotipo.RAYA}',
                confianza=0.9
            ))
        
        # 5. Espacios normales antes de % -> espacios duros
        for match in re.finditer(r'(\d)\s%', texto):
            correcciones.append(Correccion(
                tipo='reemplazo',
                posicion=match.start(),
                longitud=match.end() - match.start(),
                texto_original=match.group(0),
                texto_nuevo=f'{match.group(1)}{self.ortotipo.ESPACIO_DURO}%',
                confianza=1.0
            ))
        
        # 6. Espacios antes de unidades (km, kg, m, etc.)
        for match in re.finditer(r'(\d)\s+(km|m|cm|mm|kg|g|mg|l|ml|€|EUR|\$|USD)\b', texto, re.IGNORECASE):
            correcciones.append(Correccion(
                tipo='reemplazo',
                posicion=match.start(),
                longitud=match.end() - match.start(),
                texto_original=match.group(0),
                texto_nuevo=f'{match.group(1)}{self.ortotipo.ESPACIO_DURO}{match.group(2)}',
                confianza=1.0
            ))
        
        # 7. Dobles espacios -> espacio simple
        for match in re.finditer(r'  +', texto):
            correcciones.append(Correccion(
                tipo='reemplazo',
                posicion=match.start(),
                longitud=match.end() - match.start(),
                texto_original=match.group(0),
                texto_nuevo=' ',
                confianza=1.0
            ))
        
        return correcciones
    
    def aplicar_correccion_con_track_changes(self, parrafo: etree.Element, 
                                            correcciones: List[Correccion],
                                            tc_handler: TrackChangesHandler):
        """
        Aplica correcciones a un párrafo usando Track Changes.
        
        Args:
            parrafo: Elemento w:p (párrafo)
            correcciones: Lista de correcciones a aplicar
            tc_handler: Manejador de Track Changes
        """
        if not correcciones:
            return
        
        # Obtener todos los runs del párrafo
        runs = parrafo.findall(f"{{{NAMESPACES['w']}}}r")
        
        if not runs:
            return
        
        # Por simplicidad en MVP: reemplazar todo el texto del primer run
        # TODO: Implementar lógica más sofisticada que preserve múltiples runs
        
        primer_run = runs[0]
        texto_elemento = primer_run.find(f"{{{NAMESPACES['w']}}}t")
        
        if texto_elemento is None or not texto_elemento.text:
            return
        
        texto_original = texto_elemento.text
        
        # Aplicar todas las correcciones (de atrás hacia adelante)
        texto_corregido = texto_original
        for corr in sorted(correcciones, key=lambda c: c.posicion, reverse=True):
            if corr.posicion < len(texto_corregido):
                texto_corregido = (
                    texto_corregido[:corr.posicion] +
                    corr.texto_nuevo +
                    texto_corregido[corr.posicion + corr.longitud:]
                )
        
        # Si no hubo cambios, salir
        if texto_corregido == texto_original:
            return
        
        # Extraer formato del run original
        formato = tc_handler.extraer_formato(primer_run)
        
        # Eliminar el run original y agregar Track Changes
        parrafo.remove(primer_run)
        
        # Crear eliminación del texto original
        w_del = tc_handler.crear_eliminacion(texto_original, formato)
        parrafo.append(w_del)
        
        # Crear inserción del texto corregido
        w_ins = tc_handler.crear_insercion(texto_corregido, formato)
        parrafo.append(w_ins)
        
        self.stats['correcciones_totales'] += len(correcciones)
        self.stats['eliminaciones'] += 1
        self.stats['inserciones'] += 1
    
    def procesar_documento(self, ruta_entrada: str, ruta_salida: str):
        """
        Procesa un documento completo con Track Changes.
        
        Args:
            ruta_entrada: Ruta del documento original
            ruta_salida: Ruta del documento con Track Changes
        """
        print(f"\n📄 Procesando (Modo Profesional): {ruta_entrada}")
        print(f"👤 Autor de revisiones: {self.autor}\n")
        
        with DocxXMLHandler(ruta_entrada) as handler:
            tc = TrackChangesHandler(autor=self.autor)
            
            # Procesar cada párrafo
            parrafos = handler.obtener_parrafos()
            
            for i, parrafo in enumerate(parrafos):
                texto = handler.obtener_texto_parrafo(parrafo)
                
                if not texto.strip():
                    continue
                
                # Detectar correcciones necesarias
                correcciones = self.detectar_correcciones_ortotipo(texto)
                
                # Aplicar con Track Changes
                if correcciones:
                    self.aplicar_correccion_con_track_changes(parrafo, correcciones, tc)
                
                self.stats['parrafos_procesados'] += 1
                
                # Progreso
                if (i + 1) % 10 == 0:
                    print(f"  Procesados {i + 1} párrafos...")
            
            # Guardar documento
            handler.guardar(ruta_salida)
        
        print(f"\n✓ Documento con Track Changes guardado: {ruta_salida}")
        self.mostrar_estadisticas()
    
    def mostrar_estadisticas(self):
        """Muestra estadísticas del procesamiento."""
        print("\n📊 Estadísticas:")
        print(f"  • Párrafos procesados: {self.stats['parrafos_procesados']}")
        print(f"  • Correcciones totales: {self.stats['correcciones_totales']}")
        print(f"  • Inserciones: {self.stats['inserciones']}")
        print(f"  • Eliminaciones: {self.stats['eliminaciones']}")


if __name__ == '__main__':
    # Test rápido
    print("Test del Corrector Profesional")
    corrector = ProfessionalCorrector()
    
    # Test de detección
    texto_test = 'El portavoz dijo: "La situación es crítica".'
    correcciones = corrector.detectar_correcciones_ortotipo(texto_test)
    
    print(f"\nTexto: {texto_test}")
    print(f"Correcciones detectadas: {len(correcciones)}")
    
    for corr in correcciones:
        print(f"  - {corr.texto_original} → {corr.texto_nuevo}")
