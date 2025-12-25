"""
Herramienta de diagnóstico para ver qué detecta el corrector.
"""
from corrector_profesional import ProfessionalCorrector
from xml_handler import DocxXMLHandler
import sys

def diagnosticar_documento(ruta_docx):
    """Analiza un documento y muestra qué correcciones detectaría."""
    print(f"\n{'='*70}")
    print(f"DIAGNÓSTICO: {ruta_docx}")
    print(f"{'='*70}\n")
    
    corrector = ProfessionalCorrector()
    
    with DocxXMLHandler(ruta_docx) as handler:
        parrafos = handler.obtener_parrafos()
        
        total_correcciones = 0
        parrafos_con_cambios = 0
        
        print("📊 ANALIZANDO PÁRRAFOS...\n")
        
        for i, parrafo in enumerate(parrafos[:50]):  # Primeros 50 párrafos
            texto = handler.obtener_texto_parrafo(parrafo)
            
            if not texto.strip():
                continue
            
            correcciones = corrector.detectar_correcciones_ortotipo(texto)
            
            if correcciones:
                parrafos_con_cambios += 1
                total_correcciones += len(correcciones)
                
                print(f"Párrafo {i+1}:")
                print(f"  Original: {texto[:100]}...")
                for corr in correcciones:
                    print(f"  → {corr.texto_original} → {corr.texto_nuevo}")
                print()
        
        print(f"\n{'='*70}")
        print(f"RESUMEN:")
        print(f"  • Párrafos analizados: {min(50, len(parrafos))}")
        print(f"  • Párrafos con cambios: {parrafos_con_cambios}")
        print(f"  • Correcciones totales: {total_correcciones}")
        print(f"{'='*70}\n")
        
        if total_correcciones == 0:
            print("⚠️  NO SE DETECTARON CORRECCIONES")
            print("\nPosibles razones:")
            print("  1. El documento ya usa comillas latinas «»")
            print("  2. No hay diálogos con guiones")
            print("  3. Los porcentajes ya tienen espacio duro")
            print("\n💡 Prueba con un documento que tenga:")
            print('  • Comillas inglesas: "texto"')
            print("  • Guiones en diálogos: - Hola")
            print("  • Porcentajes: 25 %")

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Uso: python diagnostico.py documento.docx")
        sys.exit(1)
    
    diagnosticar_documento(sys.argv[1])
