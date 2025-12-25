"""
Aplicador de correcciones aprobadas con Track Changes en azul.
Preserva el formato original del documento.
"""
from xml_handler import DocxXMLHandler, NAMESPACES
from lxml import etree
from datetime import datetime
from typing import List, Dict
import json
import tempfile
import shutil
from copy import deepcopy


class AplicadorCorrecciones:
    """Aplica correcciones aprobadas con Track Changes en azul."""
    
    def __init__(self, autor: str = "Corrector Aprobado"):
        self.autor = autor
        self.color_aprobado = "0000FF"  # Azul (mejor legibilidad que verde)
        self.revision_id = 1
    
    def crear_track_change_verde(self, texto: str, formato_original: etree.Element = None) -> etree.Element:
        """
        Crea un elemento de Track Change (inserción) en azul CON SUBRAYADO.
        Copia COMPLETAMENTE el formato del run original si está disponible.
        El subrayado facilita encontrar la palabra corregida.
        """
        w_ins = etree.Element(f'{{{NAMESPACES["w"]}}}ins')
        w_ins.set(f'{{{NAMESPACES["w"]}}}id', str(self.revision_id))
        w_ins.set(f'{{{NAMESPACES["w"]}}}author', self.autor)
        w_ins.set(f'{{{NAMESPACES["w"]}}}date', datetime.now().isoformat())
        
        w_r = etree.SubElement(w_ins, f'{{{NAMESPACES["w"]}}}r')
        
        # Copiar formato del run original COMPLETAMENTE
        if formato_original is not None:
            # Hacer copia profunda del elemento rPr completo
            w_rPr_copy = deepcopy(formato_original)
            w_r.append(w_rPr_copy)
            
            # Asegurar que el color sea azul para Track Changes
            color_elem = w_rPr_copy.find(f'{{{NAMESPACES["w"]}}}color')
            if color_elem is not None:
                color_elem.set(f'{{{NAMESPACES["w"]}}}val', self.color_aprobado)
            else:
                w_color = etree.SubElement(w_rPr_copy, f'{{{NAMESPACES["w"]}}}color')
                w_color.set(f'{{{NAMESPACES["w"]}}}val', self.color_aprobado)
            
            # Añadir SUBRAYADO para resaltar la palabra corregida
            underline_elem = w_rPr_copy.find(f'{{{NAMESPACES["w"]}}}u')
            if underline_elem is not None:
                underline_elem.set(f'{{{NAMESPACES["w"]}}}val', 'single')
            else:
                w_underline = etree.SubElement(w_rPr_copy, f'{{{NAMESPACES["w"]}}}u')
                w_underline.set(f'{{{NAMESPACES["w"]}}}val', 'single')
        else:
            # Si no hay formato original, crear formato con color azul Y subrayado
            w_rPr = etree.SubElement(w_r, f'{{{NAMESPACES["w"]}}}rPr')
            w_color = etree.SubElement(w_rPr, f'{{{NAMESPACES["w"]}}}color')
            w_color.set(f'{{{NAMESPACES["w"]}}}val', self.color_aprobado)
            # Subrayado
            w_underline = etree.SubElement(w_rPr, f'{{{NAMESPACES["w"]}}}u')
            w_underline.set(f'{{{NAMESPACES["w"]}}}val', 'single')
        
        # Texto
        w_t = etree.SubElement(w_r, f'{{{NAMESPACES["w"]}}}t')
        w_t.set('{http://www.w3.org/XML/1998/namespace}space', 'preserve')
        w_t.text = texto
        
        self.revision_id += 1
        return w_ins
    
    def crear_eliminacion(self, texto: str, formato: etree.Element = None) -> etree.Element:
        """
        Crea un w:del (eliminación).
        """
        w_del = etree.Element(f"{{{NAMESPACES['w']}}}del")
        w_del.set(f"{{{NAMESPACES['w']}}}id", str(self.revision_id))
        w_del.set(f"{{{NAMESPACES['w']}}}author", self.autor)
        w_del.set(f"{{{NAMESPACES['w']}}}date", datetime.now().isoformat())
        self.revision_id += 1
        
        w_r = etree.SubElement(w_del, f"{{{NAMESPACES['w']}}}r")
        
        if formato is not None:
            w_r.append(formato)
        
        w_delText = etree.SubElement(w_r, f"{{{NAMESPACES['w']}}}delText")
        w_delText.set("{http://www.w3.org/XML/1998/namespace}space", "preserve")
        w_delText.text = texto
        
        return w_del
    
    def aplicar_correccion_a_parrafo(self, parrafo: etree.Element, texto_original: str, texto_nuevo: str):
        """
        Aplica una corrección a un párrafo específico.
        Preserva el formato del primer run encontrado.
        """
        # Obtener solo los runs que son HIJOS DIRECTOS del párrafo
        runs = parrafo.findall(f'{{{NAMESPACES["w"]}}}r')
        
        if not runs:
            return
        
        # Extraer formato del primer run (fuente, tamaño, etc.)
        primer_run = runs[0]
        formato_original = primer_run.find(f'{{{NAMESPACES["w"]}}}rPr')
        
        # Eliminar todos los runs existentes (solo hijos directos)
        for run in runs:
            try:
                parrafo.remove(run)
            except ValueError:
                pass  # Si no es hijo directo, ignorar
        
        # Encontrar la diferencia exacta entre texto_original y texto_nuevo
        # para mostrar solo la parte que cambia
        prefix_len = 0
        suffix_len = 0
        min_len = min(len(texto_original), len(texto_nuevo))
        
        # Encontrar prefijo común
        while prefix_len < min_len and texto_original[prefix_len] == texto_nuevo[prefix_len]:
            prefix_len += 1
        
        # Encontrar sufijo común
        while suffix_len < min_len - prefix_len and \
              texto_original[len(texto_original) - 1 - suffix_len] == texto_nuevo[len(texto_nuevo) - 1 - suffix_len]:
            suffix_len += 1
        
        # Extraer las partes
        prefix = texto_original[:prefix_len]
        texto_eliminado = texto_original[prefix_len:len(texto_original) - suffix_len if suffix_len > 0 else len(texto_original)]
        texto_insertado = texto_nuevo[prefix_len:len(texto_nuevo) - suffix_len if suffix_len > 0 else len(texto_nuevo)]
        suffix = texto_original[len(texto_original) - suffix_len:] if suffix_len > 0 else ""
        
        # 1. Añadir prefijo sin cambios (run normal)
        if prefix:
            w_r_prefix = etree.SubElement(parrafo, f'{{{NAMESPACES["w"]}}}r')
            if formato_original is not None:
                w_r_prefix.append(deepcopy(formato_original))
            w_t_prefix = etree.SubElement(w_r_prefix, f'{{{NAMESPACES["w"]}}}t')
            w_t_prefix.set('{http://www.w3.org/XML/1998/namespace}space', 'preserve')
            w_t_prefix.text = prefix
        
        # 2. Track Change de eliminación (SOLO la parte específica que cambia)
        if texto_eliminado:
            w_del = etree.Element(f'{{{NAMESPACES["w"]}}}del')
            w_del.set(f'{{{NAMESPACES["w"]}}}id', str(self.revision_id))
            w_del.set(f'{{{NAMESPACES["w"]}}}author', self.autor)
            w_del.set(f'{{{NAMESPACES["w"]}}}date', datetime.now().isoformat())
            self.revision_id += 1
            
            w_r_del = etree.SubElement(w_del, f'{{{NAMESPACES["w"]}}}r')
            
            if formato_original is not None:
                w_r_del.append(deepcopy(formato_original))
            
            w_delText = etree.SubElement(w_r_del, f'{{{NAMESPACES["w"]}}}delText')
            w_delText.set('{http://www.w3.org/XML/1998/namespace}space', 'preserve')
            w_delText.text = texto_eliminado
            
            parrafo.append(w_del)
        
        # 3. Track Change de inserción (SOLO la parte nueva)
        if texto_insertado:
            w_ins = self.crear_track_change_verde(texto_insertado, formato_original)
            parrafo.append(w_ins)
        
        # 4. Añadir sufijo sin cambios (run normal)
        if suffix:
            w_r_suffix = etree.SubElement(parrafo, f'{{{NAMESPACES["w"]}}}r')
            if formato_original is not None:
                w_r_suffix.append(deepcopy(formato_original))
            w_t_suffix = etree.SubElement(w_r_suffix, f'{{{NAMESPACES["w"]}}}t')
            w_t_suffix.set('{http://www.w3.org/XML/1998/namespace}space', 'preserve')
            w_t_suffix.text = suffix
    
    def aplicar_correcciones(self, ruta_entrada: str, ruta_salida: str, 
                           correcciones_aprobadas: Dict[int, Dict]):
        """
        Aplica solo las correcciones aprobadas al documento.
        VERSIÓN SIMPLIFICADA: Solo marca el párrafo completo con el texto corregido.
        """
        print(f"\n📄 Aplicando {len(correcciones_aprobadas)} correcciones...")
        
        with DocxXMLHandler(ruta_entrada) as handler:
            parrafos = handler.obtener_parrafos()
            
            # Agrupar por párrafo
            corr_por_parrafo = {}
            for corr_id, corr_data in correcciones_aprobadas.items():
                p_num = corr_data['parrafo_num']
                if p_num not in corr_por_parrafo:
                    corr_por_parrafo[p_num] = []
                corr_por_parrafo[p_num].append(corr_data)
            
            # Procesar cada párrafo
            for p_num, correcciones in corr_por_parrafo.items():
                if p_num >= len(parrafos):
                    continue
                
                parrafo = parrafos[p_num]
                texto_original = handler.obtener_texto_parrafo(parrafo)
                
                if not texto_original.strip():
                    continue
                
                # Aplicar TODAS las correcciones a este párrafo
                texto_corregido = texto_original
                for corr in correcciones:
                    # Reemplazar cada ocurrencia
                    texto_corregido = texto_corregido.replace(
                        corr['texto_original'],
                        corr['texto_nuevo'],
                        1  # Solo primera ocurrencia
                    )
                
                # Solo si hubo cambio real
                if texto_corregido != texto_original:
                    # Usar el método que hace diff y muestra solo la parte que cambia
                    self.aplicar_correccion_a_parrafo(parrafo, texto_original, texto_corregido)
            
            handler.guardar(ruta_salida)
        
        print(f"✅ Documento guardado: {ruta_salida}")


if __name__ == '__main__':
    aplicador = AplicadorCorrectoriones()
    print("✓ Aplicador inicializado")
