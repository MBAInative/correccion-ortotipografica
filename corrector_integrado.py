"""
Corrector integrado COMPLETO según normativa RAE.
Versión 3: Todas las reglas ortotipográficas y de estilo.
"""
from ortotipografia_v3 import OrtotipografiaRulesV3
from style_checker_v2 import StyleCheckerV2
from spelling_checker import SpellingChecker
from xml_handler import DocxXMLHandler, NAMESPACES
from typing import List, Dict, Tuple
import re


class Correccion:
    """Representa una corrección detectada."""
    
    def __init__(self, categoria: str, tipo: str, texto_original: str, 
                 texto_nuevo: str, explicacion: str, confianza: float,
                 contexto: str = "", parrafo_num: int = 0):
        self.categoria = categoria
        self.tipo = tipo
        self.texto_original = texto_original
        self.texto_nuevo = texto_nuevo
        self.explicacion = explicacion
        self.confianza = confianza
        self.contexto = contexto
        self.parrafo_num = parrafo_num
        self.aprobada = False
        self.id = None


class CorrectorIntegrado:
    """Corrector completo con todas las reglas RAE."""
    
    # ═══════════════════════════════════════════════════════════════
    # CATEGORÍAS COMPLETAS
    # ═══════════════════════════════════════════════════════════════
    CATEGORIAS = {
        # Ortografía
        'ortografia': 'Ortografía (LanguageTool)',
        
        # Ortotipografía
        'ortotipografia': 'Ortotipografía RAE',
        'mayusculas': 'Mayúsculas Incorrectas',
        'abreviaturas': 'Abreviaturas',
        'siglas': 'Siglas',
        'numeros': 'Formato de Números',
        'puntuacion': 'Puntuación',
        'extranjerismos': 'Extranjerismos',
        
        # Estilo
        'voz_pasiva': 'Voz Pasiva',
        'gerundios': 'Gerundios Incorrectos',
        'queismo': 'Queísmo',
        'dequeismo': 'Dequeísmo',
        'laismo': 'Laísmo',
        'loismo': 'Loísmo',
        'cosismo': 'Uso de "cosa"',
        'redundancias': 'Redundancias',
    }
    
    def __init__(self):
        print("\n🚀 Inicializando Corrector RAE Completo...")
        self.ortotipo = OrtotipografiaRulesV3()
        self.style = StyleCheckerV2()
        self.spelling = SpellingChecker()
        self.correcciones = []
        self.stats_por_categoria = {}
        print("✓ Corrector inicializado con todas las reglas RAE\n")
    
    def detectar_correcciones_ortotipo(self, texto: str, parrafo_num: int, contexto: str) -> List[Correccion]:
        """Detecta TODAS las correcciones ortotipográficas."""
        correcciones = []
        
        # Aplicar reglas en orden
        texto_actual = texto
        
        # 1. Comillas
        texto_comillas, cambios_comillas = self.ortotipo.corregir_comillas_jerarquia(texto_actual)
        if cambios_comillas > 0:
            correcciones.append(Correccion(
                categoria='ortotipografia',
                tipo='reemplazo',
                texto_original=texto_actual,
                texto_nuevo=texto_comillas,
                explicacion='Jerarquía de comillas RAE (« > " > \')',
                confianza=0.95,
                contexto=contexto,
                parrafo_num=parrafo_num
            ))
            texto_actual = texto_comillas
        
        # 2. Rayas
        texto_rayas, cambios_rayas = self.ortotipo.corregir_rayas_espaciado(texto)
        if cambios_rayas > 0 and texto_rayas != texto:
            correcciones.append(Correccion(
                categoria='ortotipografia',
                tipo='reemplazo',
                texto_original=texto,
                texto_nuevo=texto_rayas,
                explicacion='Rayas con espaciado correcto',
                confianza=0.95,
                contexto=contexto,
                parrafo_num=parrafo_num
            ))
        
        # 3. Espacios duros
        texto_espacios, cambios_espacios = self.ortotipo.corregir_espacios_duros(texto)
        if cambios_espacios > 0 and texto_espacios != texto:
            correcciones.append(Correccion(
                categoria='ortotipografia',
                tipo='reemplazo',
                texto_original=texto,
                texto_nuevo=texto_espacios,
                explicacion='Espacio duro antes de unidades',
                confianza=0.95,
                contexto=contexto,
                parrafo_num=parrafo_num
            ))
            
        # 3b. Espacios múltiples (Detección individual con contexto)
        for match in re.finditer(r'(\S+)(\s{2,})(\S+)', texto):
            texto_error = match.group(0) # "palabra1  palabra2"
            texto_corregido = f"{match.group(1)} {match.group(3)}" # "palabra1 palabra2"
            
            correcciones.append(Correccion(
                categoria='ortotipografia',
                tipo='reemplazo',
                texto_original=texto_error,
                texto_nuevo=texto_corregido,
                explicacion=f'Espacio múltiple detectado entre "{match.group(1)}" y "{match.group(3)}"',
                confianza=0.99,
                contexto=contexto,
                parrafo_num=parrafo_num
            ))
        
        # 4. Mayúsculas
        texto_mayus, cambios_mayus = self.ortotipo.corregir_mayusculas(texto)
        if cambios_mayus > 0 and texto_mayus != texto:
            correcciones.append(Correccion(
                categoria='mayusculas',
                tipo='reemplazo',
                texto_original=texto,
                texto_nuevo=texto_mayus,
                explicacion='Días/meses/estaciones en minúscula',
                confianza=0.90,
                contexto=contexto,
                parrafo_num=parrafo_num
            ))
        
        # 5. Abreviaturas
        texto_abrev, cambios_abrev = self.ortotipo.corregir_abreviaturas(texto)
        if cambios_abrev > 0 and texto_abrev != texto:
            correcciones.append(Correccion(
                categoria='abreviaturas',
                tipo='reemplazo',
                texto_original=texto,
                texto_nuevo=texto_abrev,
                explicacion='Abreviatura con punto',
                confianza=0.95,
                contexto=contexto,
                parrafo_num=parrafo_num
            ))
        
        # 6. Siglas
        texto_siglas, cambios_siglas = self.ortotipo.corregir_siglas(texto)
        if cambios_siglas > 0 and texto_siglas != texto:
            correcciones.append(Correccion(
                categoria='siglas',
                tipo='reemplazo',
                texto_original=texto,
                texto_nuevo=texto_siglas,
                explicacion='Siglas sin puntos internos',
                confianza=0.95,
                contexto=contexto,
                parrafo_num=parrafo_num
            ))
        
        # 7. Números
        texto_nums, cambios_nums = self.ortotipo.corregir_numeros(texto)
        if cambios_nums > 0 and texto_nums != texto:
            correcciones.append(Correccion(
                categoria='numeros',
                tipo='reemplazo',
                texto_original=texto,
                texto_nuevo=texto_nums,
                explicacion='Formato numérico RAE',
                confianza=0.85,
                contexto=contexto,
                parrafo_num=parrafo_num
            ))
        
        # 8. Puntuación
        texto_punt, cambios_punt = self.ortotipo.corregir_puntuacion(texto)
        if cambios_punt > 0 and texto_punt != texto:
            correcciones.append(Correccion(
                categoria='puntuacion',
                tipo='reemplazo',
                texto_original=texto,
                texto_nuevo=texto_punt,
                explicacion='Coma antes de conjunción adversativa',
                confianza=0.80,
                contexto=contexto,
                parrafo_num=parrafo_num
            ))
        
        # 9. Extranjerismos
        extranjerismos = self.ortotipo.detectar_extranjerismos(texto)
        for ext, alternativa, explicacion in extranjerismos:
            correcciones.append(Correccion(
                categoria='extranjerismos',
                tipo='reemplazo',
                texto_original=ext,
                texto_nuevo=alternativa,
                explicacion=explicacion,
                confianza=0.75,
                contexto=contexto,
                parrafo_num=parrafo_num
            ))
        
        return correcciones
    
    def analizar_documento(self, ruta_docx: str) -> Dict[str, List[Correccion]]:
        """Analiza documento con TODAS las reglas RAE."""
        print("\n🔍 Analizando documento con reglas RAE completas...\n")
        
        with DocxXMLHandler(ruta_docx) as handler:
            parrafos = handler.obtener_parrafos()
            
            for i, parrafo in enumerate(parrafos):
                texto = handler.obtener_texto_parrafo(parrafo)
                
                if not texto.strip() or len(texto) < 10:
                    continue
                
                contexto = texto[:100] + "..." if len(texto) > 100 else texto
                
                # ═══════════════════════════════════════════════════════════
                # ORTOTIPOGRAFÍA
                # ═══════════════════════════════════════════════════════════
                corr_orto = self.detectar_correcciones_ortotipo(texto, i, contexto)
                self.correcciones.extend(corr_orto)
                
                # ═══════════════════════════════════════════════════════════
                # ORTOGRAFÍA (LanguageTool)
                # ═══════════════════════════════════════════════════════════
                if self.spelling.habilitado:
                    errores_ortografia = self.spelling.detectar_errores(texto, max_errores=10)
                    for error, corr, expl in errores_ortografia:
                        self.correcciones.append(Correccion(
                            categoria='ortografia',
                            tipo='reemplazo',
                            texto_original=error,
                            texto_nuevo=corr,
                            explicacion=expl,
                            confianza=0.85,
                            contexto=contexto,
                            parrafo_num=i
                        ))
                
                # ═══════════════════════════════════════════════════════════
                # ESTILO (SpaCy + patrones)
                # ═══════════════════════════════════════════════════════════
                if len(texto) > 20:
                    resultados_estilo = self.style.analizar_estilo(texto)
                    
                    for categoria, detecciones in resultados_estilo.items():
                        for fragmento, sugerencia, explicacion in detecciones:
                            self.correcciones.append(Correccion(
                                categoria=categoria,
                                tipo='reemplazo',
                                texto_original=fragmento,
                                texto_nuevo=sugerencia,
                                explicacion=explicacion,
                                confianza=0.70,
                                contexto=contexto,
                                parrafo_num=i
                            ))
                
                if (i + 1) % 100 == 0:
                    print(f"  Analizados {i + 1} párrafos...")
        
        # Asignar IDs únicos
        for idx, corr in enumerate(self.correcciones):
            corr.id = idx
        
        # Agrupar por categoría
        correcciones_por_categoria = {}
        for categoria_key in self.CATEGORIAS.keys():
            correcciones_por_categoria[categoria_key] = [
                c for c in self.correcciones if c.categoria == categoria_key
            ]
        
        # Stats
        self.stats_por_categoria = {
            cat: len(corrs) for cat, corrs in correcciones_por_categoria.items()
        }
        
        total = sum(self.stats_por_categoria.values())
        print(f"\n✓ Análisis completado: {total} correcciones detectadas")
        
        for cat, count in self.stats_por_categoria.items():
            if count > 0:
                print(f"  • {self.CATEGORIAS[cat]}: {count}")
        
        return correcciones_por_categoria


if __name__ == '__main__':
    corrector = CorrectorIntegrado()
    print("✓ Corrector RAE completo listo")
