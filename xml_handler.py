"""
Manipulador de XML para OpenXML (formato .docx).
Permite insertar Track Changes (w:ins, w:del) directamente en el XML.
"""
from lxml import etree
from datetime import datetime
from typing import List, Tuple, Optional
import zipfile
import os
import shutil


# Namespaces de OpenXML
NAMESPACES = {
    'w': 'http://schemas.openxmlformats.org/wordprocessingml/2006/main',
    'r': 'http://schemas.openxmlformats.org/officeDocument/2006/relationships'
}


class TrackChangesHandler:
    """Manejador de Track Changes en documentos OpenXML."""
    
    def __init__(self, autor: str = "Antigravity Corrector"):
        """
        Inicializa el manejador de Track Changes.
        
        Args:
            autor: Nombre del autor de las revisiones
        """
        self.autor = autor
        self.revision_id = 0
        self.fecha = datetime.now().isoformat()
    
    def _obtener_siguiente_id(self) -> int:
        """Obtiene el siguiente ID de revisión único."""
        self.revision_id += 1
        return self.revision_id
    
    def crear_insercion(self, texto: str, formato: Optional[etree.Element] = None) -> etree.Element:
        """
        Crea un elemento <w:ins> (Track Changes insertion).
        
        Args:
            texto: Texto a insertar
            formato: Elemento w:rPr con formato (opcional)
            
        Returns:
            Elemento XML <w:ins>
        """
        # Crear elemento w:ins
        w_ins = etree.Element(f"{{{NAMESPACES['w']}}}ins")
        w_ins.set(f"{{{NAMESPACES['w']}}}id", str(self._obtener_siguiente_id()))
        w_ins.set(f"{{{NAMESPACES['w']}}}author", self.autor)
        w_ins.set(f"{{{NAMESPACES['w']}}}date", self.fecha)
        
        #Crear run (w:r) dentro de la inserción
        w_r = etree.SubElement(w_ins, f"{{{NAMESPACES['w']}}}r")
        
        # Copiar formato si existe
        if formato is not None:
            w_r.append(formato)
        
        # Crear elemento de texto (w:t)
        w_t = etree.SubElement(w_r, f"{{{NAMESPACES['w']}}}t")
        w_t.set(f"{{http://www.w3.org/XML/1998/namespace}}space", "preserve")
        w_t.text = texto
        
        return w_ins
    
    def crear_eliminacion(self, texto: str, formato: Optional[etree.Element] = None) -> etree.Element:
        """
        Crea un elemento <w:del> (Track Changes deletion).
        
        Args:
            texto: Texto a eliminar (mostrado tachado)
            formato: Elemento w:rPr con formato (opcional)
            
        Returns:
            Elemento XML <w:del>
        """
        # Crear elemento w:del
        w_del = etree.Element(f"{{{NAMESPACES['w']}}}del")
        w_del.set(f"{{{NAMESPACES['w']}}}id", str(self._obtener_siguiente_id()))
        w_del.set(f"{{{NAMESPACES['w']}}}author", self.autor)
        w_del.set(f"{{{NAMESPACES['w']}}}date", self.fecha)
        
        # Crear run (w:r) dentro de la eliminación
        w_r = etree.SubElement(w_del, f"{{{NAMESPACES['w']}}}r")
        
        # Copiar formato si existe
        if formato is not None:
            w_r_copia_formato = etree.fromstring(etree.tostring(formato))
            w_r.append(w_r_copia_formato)
        
        # Crear elemento de texto (w:delText) específico para texto eliminado
        w_del_text = etree.SubElement(w_r, f"{{{NAMESPACES['w']}}}delText")
        w_del_text.set(f"{{http://www.w3.org/XML/1998/namespace}}space", "preserve")
        w_del_text.text = texto
        
        return w_del
    
    def extraer_formato(self, run: etree.Element) -> Optional[etree.Element]:
        """
        Extrae el formato (w:rPr) de un run.
        
        Args:
            run: Elemento w:r
            
        Returns:
            Elemento w:rPr si existe, None si no
        """
        w_r_pr = run.find(f"{{{NAMESPACES['w']}}}rPr")
        if w_r_pr is not None:
            # Devolver una copia
            return etree.fromstring(etree.tostring(w_r_pr))
        return None


class DocxXMLHandler:
    """Manejador de bajo nivel para archivos .docx (OpenXML)."""
    
    def __init__(self, ruta_docx: str):
        """
        Inicializa el manejador.
        
        Args:
            ruta_docx: Ruta del archivo .docx
        """
        self.ruta_docx = ruta_docx
        self.ruta_temp = None
        self.document_xml = None
        self.tree = None
    
    def __enter__(self):
        """Context manager: abrir documento."""
        # Usar directorio temporal del sistema (evita problemas de permisos en Windows)
        import tempfile
        self.ruta_temp = tempfile.mkdtemp(prefix='docx_antigravity_')
        
        # Descomprimir .docx (es un ZIP)
        with zipfile.ZipFile(self.ruta_docx, 'r') as zip_ref:
            zip_ref.extractall(self.ruta_temp)
        
        # Cargar word/document.xml
        doc_xml_path = os.path.join(self.ruta_temp, 'word', 'document.xml')
        self.tree = etree.parse(doc_xml_path)
        self.document_xml = self.tree.getroot()
        
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager: cerrar y limpiar."""
        if self.ruta_temp and os.path.exists(self.ruta_temp):
            try:
                shutil.rmtree(self.ruta_temp, ignore_errors=True)
            except Exception:
                pass  # Silenciar errores de limpieza
        return False
    
    def guardar(self, ruta_salida: str):
        """
        Guarda el documento modificado.
        
        Args:
            ruta_salida: Ruta donde guardar el .docx
        """
        # Escribir el XML modificado
        doc_xml_path = os.path.join(self.ruta_temp, 'word', 'document.xml')
        self.tree.write(
            doc_xml_path,
            encoding='utf-8',
            xml_declaration=True,
            standalone=True
        )
        
        # Recomprimir como ZIP (.docx)
        with zipfile.ZipFile(ruta_salida, 'w', zipfile.ZIP_DEFLATED) as docx:
            for root, dirs, files in os.walk(self.ruta_temp):
                for file in files:
                    archivo_completo = os.path.join(root, file)
                    arcname = os.path.relpath(archivo_completo, self.ruta_temp)
                    docx.write(archivo_completo, arcname)
    
    def obtener_parrafos(self) -> List[etree.Element]:
        """
        Obtiene todos los párrafos (w:p) del documento.
        
        Returns:
            Lista de elementos w:p
        """
        return self.document_xml.findall(f".//{{{NAMESPACES['w']}}}p")
    
    def obtener_texto_parrafo(self, parrafo: etree.Element) -> str:
        """
        Extrae el texto de un párrafo.
        
        Args:
            parrafo: Elemento w:p
            
        Returns:
            Texto del párrafo
        """
        textos = parrafo.findall(f".//{{{NAMESPACES['w']}}}t")
        return ''.join([t.text or '' for t in textos])


def test_xml_handler():
    """Test del manejador XML."""
    print("Test de XMLHandler...")
    
    # Test de creación de Track Changes
    tc = TrackChangesHandler()
    
    # Crear inserción
    ins = tc.crear_insercion("texto nuevo")
    print("✓ Inserción creada")
    
    # Crear eliminación
    dele = tc.crear_eliminacion("texto viejo")
    print("✓ Eliminación creada")
    
    print("✓ Tests básicos pasados")


if __name__ == '__main__':
    test_xml_handler()
