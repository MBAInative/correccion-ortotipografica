"""
Utilidad para limpiar Track Changes existentes de un documento.
Acepta todas las revisiones previas para empezar con texto limpio.
"""
from lxml import etree
from xml_handler import DocxXMLHandler, NAMESPACES
import sys


def limpiar_track_changes(ruta_docx, ruta_salida):
    """
    Acepta todos los Track Changes existentes en un documento.
    Elimina w:ins, w:del, w:moveFrom, w:moveTo.
    """
    print(f"\n🧹 Limpiando Track Changes de: {ruta_docx}")
    
    with DocxXMLHandler(ruta_docx) as handler:
        parrafos = handler.obtener_parrafos()
        cambios_removidos = 0
        
        for parrafo in parrafos:
            # Buscar y aceptar inserciones (w:ins)
            for w_ins in parrafo.findall(f".//{{{NAMESPACES['w']}}}ins"):
                # Extraer los runs de dentro de w:ins
                runs_internos = w_ins.findall(f"{{{NAMESPACES['w']}}}r")
                
                # Insertar los runs directamente en el párrafo
                parent = w_ins.getparent()
                index = list(parent).index(w_ins)
                
                for run in runs_internos:
                    parent.insert(index, run)
                    index += 1
                
                # Eliminar el w:ins
                parent.remove(w_ins)
                cambios_removidos += 1
            
            # Buscar y eliminar eliminaciones (w:del)
            for w_del in parrafo.findall(f".//{{{NAMESPACES['w']}}}del"):
                parent = w_del.getparent()
                parent.remove(w_del)
                cambios_removidos += 1
            
            # Eliminar moveFrom y moveTo también
            for w_move in parrafo.findall(f".//{{{NAMESPACES['w']}}}moveFrom"):
                parent = w_move.getparent()
                parent.remove(w_move)
                cambios_removidos += 1
            
            for w_move in parrafo.findall(f".//{{{NAMESPACES['w']}}}moveTo"):
                parent = w_move.getparent()
                parent.remove(w_move)
                cambios_removidos += 1
        
        handler.guardar(ruta_salida)
    
    print(f"✅ Track Changes removidos: {cambios_removidos}")
    print(f"✅ Documento limpio guardado: {ruta_salida}")


if __name__ == '__main__':
    if len(sys.argv) < 3:
        print("Uso: python limpiar_tc.py documento.docx salida.docx")
        sys.exit(1)
    
    limpiar_track_changes(sys.argv[1], sys.argv[2])
