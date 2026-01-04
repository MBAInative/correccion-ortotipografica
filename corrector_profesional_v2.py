"""
Versión mejorada del corrector profesional con mejor manejo de XML.
"""
from xml_handler import DocxXMLHandler, TrackChangesHandler, NAMESPACES
from ortotipografia import OrtotipografiaRules
from spellchecker import SpellChecker
from lxml import etree
from typing import List, Tuple, Dict
import re


class Correccion:
    """Representa una corrección a aplicar."""
    
    def __init__(self, tipo: str, posicion: int, longitud: int, 
                 texto_original: str, texto_nuevo: str, confianza: float = 1.0):
        self.tipo = tipo
        self.posicion = posicion
        self.longitud = longitud
        self.texto_original = texto_original
        self.texto_nuevo = texto_nuevo
        self.confianza = confianza


class ProfessionalCorrectorV2:
    """Corrector profesional mejorado con mejor detección."""
    
    def __init__(self, autor: str = "Antigravity Corrector"):
        self.autor = autor
        self.ortotipo = OrtotipografiaRules()
        try:
            print("⏳ Inicializando diccionario (pyspellchecker)...")
            self.spell = SpellChecker(language='es')
            print("✓ Diccionario listo")
        except Exception as e:
            print(f"⚠️ Error cargando diccionario: {e}")
            self.spell = None

        self.stats = {
            'correcciones_totales': 0,
            'parrafos_procesados': 0,
            'parrafos_modificados': 0
        }
    
    def corregir_ortografia(self, texto: str) -> str:
        """
        Corrige ortografía palabra por palabra usando diccionario.
        Ignora palabras que empiezan con mayúscula (asume nombres propios).
        """
        if not self.spell:
            return texto
            
        # Tokenizar manteniendo delimitadores para reconstruir
        # \b no sirve bien aquí porque queremos separar signos de puntuación
        # Dividimos por caracteres que no sean letras
        tokens = re.split(r'([^\w\u00C0-\u017F]+)', texto)
        
        texto_corregido = []
        
        for token in tokens:
            # Si no es palabra o está vacía, añadir tal cual
            if not token or not token.isalpha():
                texto_corregido.append(token)
                continue
                
            # Criterio: Solo corregir palabras en minúscula (no nombres propios)
            # Esto cumple el requisito: "revisar cada palabra que no sea nombre propio"
            if token[0].islower():
                # Verificar si está en el diccionario
                # unknown() devuelve un set de palabras desconocidas
                if token.lower() in self.spell.unknown([token.lower()]):
                    # Obtener corrección
                    correccion = self.spell.correction(token.lower())
                    if correccion and correccion != token.lower():
                        # Mantener casing original si fuera necesario (aquí es lowercase)
                        texto_corregido.append(correccion)
                    else:
                        texto_corregido.append(token)
                else:
                    texto_corregido.append(token)
            else:
                # Es mayúscula/Nombre propio - dejar tal cual
                texto_corregido.append(token)
                
        return "".join(texto_corregido)

    def detectar_y_corregir_texto(self, texto: str) -> Tuple[str, int]:
        """
        Detecta y aplica correcciones a un texto.
        Retorna el texto corregido y el número de correcciones.
        """
        texto_original = texto
        cambios = 0
        
        # 1. Aplicar correcciones de ortotipografía (incluye espacios múltiples)
        texto_temp = self.ortotipo.aplicar_todas(texto)
        
        # 2. Aplicar corrección ortográfica (diccionario)
        texto_corregido = self.corregir_ortografia(texto_temp)
        
        if texto_corregido != texto_original:
            cambios = 1
        
        return texto_corregido, cambios
    
    def procesar_run_con_track_changes(self, run: etree.Element, texto_nuevo: str, 
                                       parrafo: etree.Element, tc: TrackChangesHandler):
        """Reemplaza un run con Track Changes."""
        # Obtener texto original
        texto_elem = run.find(f"{{{NAMESPACES['w']}}}t")
        if texto_elem is None:
            return
        
        texto_original = texto_elem.text or ""
        
        # Extraer formato
        formato = tc.extraer_formato(run)
        
        # Obtener posición del run en el párrafo
        run_index = list(parrafo).index(run)
        
        # Crear eliminación
        w_del = tc.crear_eliminacion(texto_original, formato)
        
        # Crear inserción
        w_ins = tc.crear_insercion(texto_nuevo, formato)
        
        # Insertar después del run original
        parrafo.insert(run_index + 1, w_del)
        parrafo.insert(run_index + 2, w_ins)
        
        # Eliminar run original
        parrafo.remove(run)
    
    def limpiar_track_changes_existentes(self, handler):
        """Limpia todos los Track Changes existentes del documento."""
        parrafos = handler.obtener_parrafos()
        cambios_removidos = 0
        
        for parrafo in parrafos:
            # Aceptar inserciones (w:ins) - extraer contenido
            for w_ins in list(parrafo.findall(f".//{{{NAMESPACES['w']}}}ins")):
                runs_internos = w_ins.findall(f"{{{NAMESPACES['w']}}}r")
                parent = w_ins.getparent()
                index = list(parent).index(w_ins)
                
                for run in runs_internos:
                    parent.insert(index, run)
                    index += 1
                
                parent.remove(w_ins)
                cambios_removidos += 1
            
            # Rechazar eliminaciones (w:del) - eliminar completamente
            for w_del in list(parrafo.findall(f".//{{{NAMESPACES['w']}}}del")):
                parent = w_del.getparent()
                parent.remove(w_del)
                cambios_removidos += 1
            
            # Eliminar moveFrom/moveTo
            for tag in ['moveFrom', 'moveTo']:
                for elem in list(parrafo.findall(f".//{{{NAMESPACES['w']}}}{tag}")):
                    parent = elem.getparent()
                    parent.remove(elem)
                    cambios_removidos += 1
        
        return cambios_removidos
    
    def procesar_documento(self, ruta_entrada: str, ruta_salida: str):
        """Procesa documento con Track Changes mejorado."""
        print(f"\n📄 Procesando (Modo Profesional V2): {ruta_entrada}")
        print(f"👤 Autor: {self.autor}\n")
        
        with DocxXMLHandler(ruta_entrada) as handler:
            # PASO 1: Limpiar Track Changes antiguos
            print("🧹 Limpiando Track Changes previos...")
            tc_antiguos = self.limpiar_track_changes_existentes(handler)
            print(f"   Removidos: {tc_antiguos} track changes antiguos\n")
            
            # PASO 2: Crear nuevos Track Changes
            tc = TrackChangesHandler(autor=self.autor)
            parrafos = handler.obtener_parrafos()
            
            print("🔍 Detectando correcciones ortotipográficas...\n")
            
            for i, parrafo in enumerate(parrafos):
                # Obtener todos los runs del párrafo
                runs = parrafo.findall(f"{{{NAMESPACES['w']}}}r")
                
                if not runs:
                    continue
                
                # Procesar cada run
                for run in list(runs):  # list() para evitar problemas al modificar
                    texto_elem = run.find(f"{{{NAMESPACES['w']}}}t")
                    if texto_elem is None or not texto_elem.text:
                        continue
                    
                    texto_original = texto_elem.text
                    texto_corregido, cambios = self.detectar_y_corregir_texto(texto_original)
                    
                    if cambios > 0:
                        self.procesar_run_con_track_changes(run, texto_corregido, parrafo, tc)
                        self.stats['correcciones_totales'] += 1
                        self.stats['parrafos_modificados'] += 1
                
                self.stats['parrafos_procesados'] += 1
                
                if (i + 1) % 100 == 0:
                    print(f"  Procesados {i + 1} párrafos...")
            
            handler.guardar(ruta_salida)
        
        print(f"\n✓ Guardado: {ruta_salida}")
        self.mostrar_estadisticas()

    
    def mostrar_estadisticas(self):
        print(f"\n📊 Estadísticas:")
        print(f"  • Párrafos procesados: {self.stats['parrafos_procesados']}")
        print(f"  • Párrafos modificados: {self.stats['parrafos_modificados']}")
        print(f"  • Correcciones totales: {self.stats['correcciones_totales']}")


if __name__ == '__main__':
    corrector = ProfessionalCorrectorV2()
    print("Test del Corrector Profesional V2")
    
    texto_test = 'El portavoz dijo: "La situación es crítica". El crecimiento fue del 25 %.'
    resultado, cambios = corrector.detectar_y_corregir_texto(texto_test)
    
    print(f"\nOriginal: {texto_test}")
    print(f"Corregido: {resultado}")
    print(f"Cambios: {cambios}")
