"""
CLI principal - Versión integrada con ambas fases.
"""
import sys
import argparse
from pathlib import Path
from corrector import BasicCorrector
from corrector_profesional import ProfessionalCorrector


def main():
    """Función principal del CLI."""
    parser = argparse.ArgumentParser(
        description='Corrector ortotipográfico y de estilo para documentos .docx',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Ejemplos de uso:
  
  Modo básico (correcciones directas):
    python main.py documento.docx
  
  Modo profesional (Track Changes):
    python main.py documento.docx --profesional
    python main.py documento.docx -p -o corregido.docx
    
  Opciones adicionales:
    python main.py documento.docx --autor "Juan Pérez"
        """
    )
    
    parser.add_argument(
        'archivo_entrada',
        type=str,
        help='Ruta del archivo .docx a corregir'
    )
    
    parser.add_argument(
        '-o', '--output',
        type=str,
        default=None,
        help='Ruta del archivo de salida'
    )
    
    parser.add_argument(
        '-p', '--profesional',
        action='store_true',
        help='Usar modo profesional con Track Changes'
    )
    
    parser.add_argument(
        '--autor',
        type=str,
        default='Antigravity Corrector',
        help='Autor de las revisiones (modo profesional)'
    )
    
    parser.add_argument(
        '--idioma',
        type=str,
        default='es',
        choices=['es', 'es-ES', 'es-AR', 'es-MX'],
        help='Variante de idioma para LanguageTool'
    )
    
    parser.add_argument(
        '--version',
        action='version',
        version='%(prog)s 2.0 (Fase Profesional)'
    )
    
    args = parser.parse_args()
    
    # Validar archivo de entrada
    ruta_entrada = Path(args.archivo_entrada)
    if not ruta_entrada.exists():
        print(f"❌ Error: El archivo '{args.archivo_entrada}' no existe")
        sys.exit(1)
    
    if ruta_entrada.suffix.lower() != '.docx':
        print(f"❌ Error: El archivo debe ser .docx (recibido: {ruta_entrada.suffix})")
        sys.exit(1)
    
    # Determinar archivo de salida
    if args.output:
        ruta_salida = Path(args.output)
    else:
        sufijo = '_tc' if args.profesional else '_corregido'
        ruta_salida = ruta_entrada.parent / f"{ruta_entrada.stem}{sufijo}{ruta_entrada.suffix}"
    
    # Mostrar banner
    print("=" * 70)
    if args.profesional:
        print("  CORRECTOR ORTOTIPOGRÁFICO - Modo Profesional (Track Changes)")
    else:
        print("  CORRECTOR ORTOTIPOGRÁFICO - Modo Básico")
    print("=" * 70)
    
    # Procesar según modo
    try:
        if args.profesional:
            # Modo profesional: Track Changes
            corrector = ProfessionalCorrector(autor=args.autor)
            corrector.procesar_documento(str(ruta_entrada), str(ruta_salida))
        else:
            # Modo básico: correcciones directas
            corrector = BasicCorrector(idioma=args.idioma)
            corrector.configurar_reglas()
            corrector.procesar_documento(str(ruta_entrada), str(ruta_salida))
            corrector.cerrar()
        
        print("\n" + "=" * 70)
        print("  ✓ PROCESO COMPLETADO")
        print("=" * 70)
        
        if args.profesional:
            print(f"\n💡 Abre el documento en Word y revisa las revisiones")
            print(f"   Menú: Revisar → Control de cambios → Aceptar/Rechazar")
        
    except Exception as e:
        print(f"\n❌ Error durante el procesamiento: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == '__main__':
    main()
